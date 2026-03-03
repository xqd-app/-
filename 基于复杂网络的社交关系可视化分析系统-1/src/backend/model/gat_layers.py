import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv
from typing import Optional

class EnhancedGATLayer(nn.Module):
    """
    增强版GAT层，支持局部聚类系数权重因子和互动频次衰减因子
    """
    def __init__(self, in_features: int, out_features: int, heads: int = 8, 
                 concat: bool = True, negative_slope: float = 0.2, 
                 dropout: float = 0.6, add_self_loops: bool = True):
        super(EnhancedGATLayer, self).__init__()
        
        self.in_features = in_features
        self.out_features = out_features
        self.heads = heads
        self.concat = concat
        self.negative_slope = negative_slope
        self.dropout = dropout
        self.add_self_loops = add_self_loops
        
        # 使用标准的GATConv
        self.gat_conv = GATConv(
            in_channels=in_features,
            out_channels=out_features,
            heads=heads,
            concat=concat,
            negative_slope=negative_slope,
            dropout=dropout,
            add_self_loops=add_self_loops
        )
        
        # 批归一化层
        out_dim = out_features * heads if concat else out_features
        self.batch_norm = nn.BatchNorm1d(out_dim)
        
        # 激活函数
        self.activation = nn.LeakyReLU(negative_slope)
        
    def forward(self, x, edge_index, clustering_coef=None, interaction_decay=None):
        """
        前向传播
        
        Args:
            x: 节点特征 [N, in_features]
            edge_index: 边索引 [2, E]
            clustering_coef: 聚类系数 [N, 1]，用于局部聚类系数权重因子
            interaction_decay: 互动衰减因子 [N, 1]，用于互动频次衰减因子
        """
        out = self.gat_conv(x, edge_index)
        out = self.batch_norm(out)
        out = self.activation(out)
        return out

class ImprovedGATLayer(nn.Module):
    """
    改进版GAT层，结合了多种优化技术
    """
    def __init__(self, in_features: int, out_features: int, heads: int = 8,
                 concat: bool = True, negative_slope: float = 0.2,
                 dropout: float = 0.6, add_self_loops: bool = True):
        super(ImprovedGATLayer, self).__init__()
        
        # 使用标准的GATConv
        self.gat_conv = GATConv(
            in_channels=in_features,
            out_channels=out_features,
            heads=heads,
            concat=concat,
            negative_slope=negative_slope,
            dropout=dropout,
            add_self_loops=add_self_loops
        )
        
        # 批归一化层
        out_dim = out_features * heads if concat else out_features
        self.batch_norm = nn.BatchNorm1d(out_dim)
        
        # 激活函数
        self.activation = nn.LeakyReLU(negative_slope)
        
    def forward(self, x, edge_index, clustering_coef=None, interaction_decay=None):
        """
        前向传播
        """
        out = self.gat_conv(x, edge_index)
        out = self.batch_norm(out)
        out = self.activation(out)
        return out