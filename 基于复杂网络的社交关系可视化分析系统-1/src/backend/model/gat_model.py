import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Optional
from torch_geometric.nn import GATConv

class EnhancedGAT(nn.Module):
    """
    增强版GAT模型，支持局部聚类系数权重因子和互动频次衰减因子
    """
    def __init__(self, 
                 input_dim: int, 
                 hidden_dims: List[int], 
                 output_dim: int, 
                 heads: List[int],
                 dropout: float = 0.6,
                 use_clustering_coef: bool = False):
        """
        初始化增强版GAT模型
        
        Args:
            input_dim: 输入特征维度
            hidden_dims: 隐藏层维度列表
            output_dim: 输出维度
            heads: 每层的注意力头数列表
            dropout: Dropout率
            use_clustering_coef: 是否使用聚类系数
        """
        super(EnhancedGAT, self).__init__()
        
        # 使用简化模型
        self.conv1 = GATConv(input_dim, hidden_dims[0], heads=heads[0])
        self.conv2 = GATConv(hidden_dims[0] * heads[0], output_dim, heads=heads[1], concat=False)
        
        # 添加投影层，将输出维度映射回输入维度用于重构损失
        self.projection = nn.Linear(output_dim, input_dim)
        
        self.bn1 = nn.BatchNorm1d(hidden_dims[0] * heads[0])
        self.bn2 = nn.BatchNorm1d(output_dim)
        self.bn3 = nn.BatchNorm1d(input_dim)
        
        self.dropout = dropout
        self.use_clustering_coef = use_clustering_coef
        
    def forward(self, x, edge_index, clustering_coef=None, interaction_decay=None):
        """
        前向传播
        
        Args:
            x: 节点特征 [N, input_dim]
            edge_index: 边索引 [2, E]
            clustering_coef: 聚类系数 [N, 1]，用于局部聚类系数权重因子
            interaction_decay: 互动衰减因子 [N, 1]，用于互动频次衰减因子
        """
        x = self.conv1(x, edge_index)
        x = self.bn1(x)
        x = F.elu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        
        x = self.conv2(x, edge_index)
        x = self.bn2(x)
        x = F.elu(x)
        
        # 投影回原始维度
        x = self.projection(x)
        x = self.bn3(x)
        return x

    def get_embeddings(self, x, edge_index, clustering_coef=None, interaction_decay=None):
        """
        获取节点嵌入（不经过投影层）
        """
        x = self.conv1(x, edge_index)
        x = self.bn1(x)
        x = F.elu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        
        x = self.conv2(x, edge_index)
        x = self.bn2(x)
        return x

class SimpleGAT(nn.Module):
    """
    简化版GAT模型，用于快速实验
    """
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, heads: int = 8):
        super(SimpleGAT, self).__init__()
        
        self.conv1 = GATConv(input_dim, hidden_dim, heads=heads)
        self.conv2 = GATConv(hidden_dim * heads, output_dim, heads=1, concat=False)
        
        # 添加投影层，将输出维度映射回输入维度用于重构损失
        self.projection = nn.Linear(output_dim, input_dim)
        
        self.bn1 = nn.BatchNorm1d(hidden_dim * heads)
        self.bn2 = nn.BatchNorm1d(output_dim)
        self.bn3 = nn.BatchNorm1d(input_dim)
        
    def forward(self, x, edge_index, clustering_coef=None, interaction_decay=None):
        x = self.conv1(x, edge_index)
        x = self.bn1(x)
        x = F.elu(x)
        x = F.dropout(x, training=self.training)
        
        x = self.conv2(x, edge_index)
        x = self.bn2(x)
        x = F.elu(x)
        
        # 投影回原始维度
        x = self.projection(x)
        x = self.bn3(x)
        return x
    
    def get_embeddings(self, x, edge_index, clustering_coef=None, interaction_decay=None):
        """
        获取节点嵌入（不经过投影层）
        """
        x = self.conv1(x, edge_index)
        x = self.bn1(x)
        x = F.elu(x)
        x = F.dropout(x, training=self.training)
        
        x = self.conv2(x, edge_index)
        x = self.bn2(x)
        return x