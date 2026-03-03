"""
GAT模型训练器模块
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from typing import Dict, Any, Optional
import json
import os
from src.backend.model.gat_model import SimpleGAT
import numpy as np

class EarlyStopping:
    """
    早停机制
    """
    def __init__(self, patience: int = 50, min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float('inf')
        
    def __call__(self, val_loss: float) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            
        return self.counter >= self.patience

class GATTrainer:
    """
    GAT模型训练器
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # 从配置中提取参数
        self.learning_rate = getattr(config, 'learning_rate', 0.001)
        self.weight_decay = getattr(config, 'weight_decay', 5e-4)
        self.beta1 = getattr(config, 'beta1', 0.9)
        self.beta2 = getattr(config, 'beta2', 0.999)
        self.epochs = getattr(config, 'epochs', 1000)
        self.patience = getattr(config, 'patience', 100)
        self.scheduler_factor = getattr(config, 'scheduler_factor', 0.5)
        self.scheduler_patience = getattr(config, 'scheduler_patience', 50)
        self.gradient_clip = getattr(config, 'gradient_clip', 1.0)
        self.log_interval = getattr(config, 'log_interval', 10)
        self.save_checkpoints = getattr(config, 'save_checkpoints', True)
        self.checkpoint_dir = getattr(config, 'checkpoint_dir', './checkpoints')
        
        # 创建模型 - 使用SimpleGAT
        self.model = SimpleGAT(
            input_dim=config.input_dim,
            hidden_dim=32,  # 固定隐藏层维度
            output_dim=config.output_dim,
            heads=4  # 固定注意力头数
        )
        
        # 设置设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # 优化器
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
            betas=(self.beta1, self.beta2)
        )
        
        # 学习率调度器
        self.scheduler = ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=self.scheduler_factor,
            patience=self.scheduler_patience,
            verbose=True
        )
        
        # 早停机制
        self.early_stopping = EarlyStopping(patience=self.patience)
        
        # 损失历史
        self.train_losses = []
        self.val_losses = []
        
    def train(self, data):
        """
        训练模型
        """
        best_val_loss = float('inf')
        best_model_state = None
        
        print(f"开始训练模型，共 {self.epochs} 轮")
        print(f"使用设备: {self.device}")
        
        for epoch in range(self.epochs):
            # 训练阶段
            self.model.train()
            self.optimizer.zero_grad()
            
            # 前向传播
            out = self.model(
                data.x.to(self.device), 
                data.edge_index.to(self.device)
            )
            
            # 计算损失（重构损失）
            loss = self.reconstruction_loss(out, data.x.to(self.device))
            
            # 反向传播
            loss.backward()
            
            # 梯度裁剪
            if self.gradient_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip)
            
            # 更新参数
            self.optimizer.step()
            
            # 验证阶段
            val_loss = self.validate(data)
            
            # 记录损失
            self.train_losses.append(loss.item())
            self.val_losses.append(val_loss)
            
            # 更新学习率
            self.scheduler.step(val_loss)
            
            # 日志输出
            if epoch % self.log_interval == 0:
                print(f'Epoch: {epoch:03d}, Train Loss: {loss:.4f}, Val Loss: {val_loss:.4f}')
            
            # 保存最佳模型
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_state = self.model.state_dict().copy()
                
                # 保存检查点
                if self.save_checkpoints:
                    self.save_checkpoint(epoch, val_loss)
            
            # 早停检查
            if self.early_stopping(val_loss):
                print(f"早停机制触发，停止训练在第 {epoch} 轮")
                break
        
        # 恢复最佳模型
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)
            
        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }
    
    def reconstruction_loss(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        重构损失函数
        """
        return nn.MSELoss()(pred, target)
    
    def validate(self, data) -> float:
        """
        验证模型
        """
        self.model.eval()
        with torch.no_grad():
            out = self.model(
                data.x.to(self.device), 
                data.edge_index.to(self.device)
            )
            loss = self.reconstruction_loss(out, data.x.to(self.device))
        return loss.item()
    
    def get_node_embeddings(self, data) -> torch.Tensor:
        """
        获取节点嵌入
        """
        self.model.eval()
        with torch.no_grad():
            embeddings = self.model.get_embeddings(
                data.x.to(self.device), 
                data.edge_index.to(self.device)
            )
        return embeddings.cpu()
    
    def save_model(self, path: str = '../models/gat_model.pth'):
        """
        保存模型
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config.__dict__ if hasattr(self.config, '__dict__') else self.config,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }, path)
        
        print(f"模型已保存到: {path}")
    
    def save_checkpoint(self, epoch: int, val_loss: float):
        """
        保存检查点
        """
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        checkpoint_path = os.path.join(self.checkpoint_dir, f'checkpoint_epoch_{epoch}.pth')
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'val_loss': val_loss
        }, checkpoint_path)
    
    def load_model(self, path: str = '../models/gat_model.pth'):
        """
        加载模型
        """
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if 'train_losses' in checkpoint:
            self.train_losses = checkpoint['train_losses']
            self.val_losses = checkpoint['val_losses']
            
        print(f"模型已从 {path} 加载")

def set_random_seed(seed: int):
    """
    设置随机种子
    """
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
