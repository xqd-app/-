"""
更新后的配置加载模块
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import yaml
import os

@dataclass
class GATConfig:
    """
    GAT模型配置类
    """
    # 模型架构参数
    input_dim: int = 9  # 默认改为9维
    hidden_dims: List[int] = None
    output_dim: int = 64
    heads: List[int] = None
    dropout: float = 0.6
    use_clustering_coef: bool = False
    use_interaction_decay: bool = False
    
    # 训练参数
    learning_rate: float = 0.001
    weight_decay: float = 5e-4
    beta1: float = 0.9
    beta2: float = 0.999
    epochs: int = 1000
    batch_size: int = 32
    train_val_split: float = 0.8
    random_seed: int = 42
    
    # 学习率调度参数
    scheduler_factor: float = 0.5
    scheduler_patience: int = 50
    
    # 早停机制参数
    early_stopping: bool = True
    patience: int = 100
    
    # 梯度裁剪参数
    gradient_clip: float = 1.0
    
    # 检查点保存参数
    save_checkpoints: bool = True
    checkpoint_dir: str = './checkpoints'
    
    # 日志记录参数
    log_interval: int = 10
    
    # 系统配置
    device: str = "auto"
    log_level: str = "INFO"
    model_output_path: str = "models/"
    
    def __post_init__(self):
        """
        初始化默认值
        """
        if self.hidden_dims is None:
            self.hidden_dims = [128, 64]  # 修改为适合9维输入的配置
        if self.heads is None:
            self.heads = [8, 8, 1]
    
    @classmethod
    def from_main_config(cls, main_config_path: str = '../config/config.yaml'):
        """从主配置文件加载模型配置"""
        with open(main_config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        # 提取模型训练配置
        model_training = config_dict.get('model_training', {})
        gat_config = model_training.get('gat', {})
        training_config = model_training.get('training', {})
        data_config = model_training.get('data_preprocessing', {})
        
        # 提取系统配置
        system_config = config_dict.get('system', {})
        data_path_config = config_dict.get('data', {})
        
        # 合并配置
        merged_config = {
            **gat_config,
            **training_config,
            **data_config,
            'device': system_config.get('device', 'auto'),
            'model_output_path': data_path_config.get('model_output_path', 'models/'),
            'scheduler_factor': gat_config.get('scheduler_factor', 0.5),
            'scheduler_patience': gat_config.get('scheduler_patience', 50),
            'gradient_clip': gat_config.get('gradient_clip', 1.0),
            'save_checkpoints': gat_config.get('save_checkpoints', True),
            'checkpoint_dir': gat_config.get('checkpoint_dir', './checkpoints'),
            'log_interval': gat_config.get('log_interval', 10),
            'use_interaction_decay': gat_config.get('use_interaction_decay', False)
        }
        
        return cls(**merged_config)
    
    @classmethod
    def from_model_config(cls, model_config_path: str = '../config/model_config.yaml'):
        """从专用模型配置文件加载配置"""
        if not os.path.exists(model_config_path):
            print(f"模型配置文件不存在: {model_config_path}，使用默认配置")
            return cls()
        
        with open(model_config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        # 提取各部分的配置
        gat_arch = config_dict.get('gat_architecture', {})
        training_params = config_dict.get('training_params', {})
        data_config = config_dict.get('data_config', {})
        output_config = config_dict.get('output_config', {})
        system_config = config_dict.get('system_config', {})
        
        # 构建配置字典
        config_dict = {
            # 架构配置
            'input_dim': gat_arch.get('input_dim', 7),
            'output_dim': gat_arch.get('output_dim', 64),
            'hidden_dims': gat_arch.get('hidden_dims', [256, 128]),
            'heads': gat_arch.get('heads', [8, 8, 1]),
            'dropout': gat_arch.get('dropout', 0.6),
            'use_clustering_coef': gat_arch.get('use_clustering_coef', False),
            'use_interaction_decay': gat_arch.get('use_interaction_decay', False),
            
            # 训练配置
            'learning_rate': training_params.get('learning_rate', 0.001),
            'weight_decay': training_params.get('weight_decay', 5e-4),
            'beta1': training_params.get('beta1', 0.9),
            'beta2': training_params.get('beta2', 0.999),
            'epochs': training_params.get('epochs', 1000),
            'batch_size': training_params.get('batch_size', 32),
            'early_stopping': training_params.get('early_stopping', True),
            'patience': training_params.get('patience', 100),
            'scheduler_factor': training_params.get('scheduler_factor', 0.5),
            'scheduler_patience': training_params.get('scheduler_patience', 50),
            'gradient_clip': training_params.get('gradient_clip', 1.0),
            'save_checkpoints': training_params.get('save_checkpoints', True),
            'checkpoint_dir': training_params.get('checkpoint_dir', './checkpoints'),
            'log_interval': training_params.get('log_interval', 10),
            
            # 数据配置
            'train_val_split': data_config.get('train_val_split', 0.8),
            'random_seed': data_config.get('random_seed', 42),
            
            # 系统配置
            'device': system_config.get('device', 'auto'),
            'model_output_path': output_config.get('model_dir', 'models/')
        }
        
        return cls(**config_dict)
    
    @classmethod
    def load_config(cls, config_path: str = None):
        """智能加载配置（优先使用专用配置）"""
        if config_path:
            if 'model_config' in config_path:
                return cls.from_model_config(config_path)
            else:
                return cls.from_main_config(config_path)
        
        # 默认加载顺序
        model_config_path = '../config/model_config.yaml'
        main_config_path = '../config/config.yaml'
        
        if os.path.exists(model_config_path):
            print(f"加载专用模型配置: {model_config_path}")
            return cls.from_model_config(model_config_path)
        elif os.path.exists(main_config_path):
            print(f"加载主配置文件中的模型配置: {main_config_path}")
            return cls.from_main_config(main_config_path)
        else:
            print("未找到配置文件，使用默认配置")
            return cls()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'input_dim': self.input_dim,
            'output_dim': self.output_dim,
            'hidden_dims': self.hidden_dims,
            'heads': self.heads,
            'dropout': self.dropout,
            'use_clustering_coef': self.use_clustering_coef,
            'use_interaction_decay': self.use_interaction_decay,
            'learning_rate': self.learning_rate,
            'weight_decay': self.weight_decay,
            'beta1': self.beta1,
            'beta2': self.beta2,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'early_stopping': self.early_stopping,
            'patience': self.patience,
            'scheduler_factor': self.scheduler_factor,
            'scheduler_patience': self.scheduler_patience,
            'gradient_clip': self.gradient_clip,
            'save_checkpoints': self.save_checkpoints,
            'checkpoint_dir': self.checkpoint_dir,
            'log_interval': self.log_interval,
            'train_val_split': self.train_val_split,
            'random_seed': self.random_seed,
            'device': self.device,
            'model_output_path': self.model_output_path
        }
    
    def save(self, path: str):
        """保存配置到YAML文件"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)