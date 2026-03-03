"""
数据加载和处理模块
"""
import numpy as np
import torch
from torch_geometric.data import Data
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict, Optional
import json
import os
import pandas as pd


class GATDataLoader:
    """GAT模型数据加载器"""
    
    def __init__(self, data_dir: str = '../data/processed/'):
        # 规范化路径
        self.data_dir = os.path.normpath(data_dir)
        self.scaler = StandardScaler()
        self.node_features = None
        self.edge_index = None
        self.clustering_coef = None
        
    def load_data(self) -> Dict[str, np.ndarray]:
        """
        从文件加载所有数据
        
        Returns:
            数据字典
        """
        data = {}
        
        try:
            # 加载节点特征
            features_path = os.path.join(self.data_dir, 'node_features.npy')
            # 首先尝试加载9维特征
            features_9d_path = os.path.join(self.data_dir, 'node_features_9d.npy')
            if os.path.exists(features_9d_path):
                self.node_features = np.load(features_9d_path)
                data['features'] = self.node_features
                print(f"加载9维节点特征: {self.node_features.shape}")
            elif os.path.exists(features_path):
                self.node_features = np.load(features_path)
                data['features'] = self.node_features
                print(f"加载节点特征: {self.node_features.shape}")
            else:
                # 如果npy文件不存在，尝试从csv加载
                csv_features_path = os.path.join(self.data_dir, 'node_features.csv')
                csv_features_9d_path = os.path.join(self.data_dir, 'node_features_9d.csv')
                if os.path.exists(csv_features_9d_path):
                    df = pd.read_csv(csv_features_9d_path)
                    self.node_features = df.values
                    data['features'] = self.node_features
                    print(f"从CSV加载9维节点特征: {self.node_features.shape}")
                    # 同时保存为npy格式供下次使用
                    np.save(features_9d_path, self.node_features)
                    print(f"已保存为9维NPY文件: {features_9d_path}")
                elif os.path.exists(csv_features_path):
                    df = pd.read_csv(csv_features_path)
                    self.node_features = df.values
                    data['features'] = self.node_features
                    print(f"从CSV加载节点特征: {self.node_features.shape}")
                    # 同时保存为npy格式供下次使用
                    np.save(features_path, self.node_features)
                    print(f"已保存为NPY文件: {features_path}")
                else:
                    raise ValueError("未能找到任何节点特征文件")
            
            # 加载邻接矩阵并转换为边索引
            adj_path = os.path.join(self.data_dir, 'adjacency_matrix.npy')
            if os.path.exists(adj_path):
                adjacency_matrix = np.load(adj_path)
                self.edge_index = self._adjacency_to_edge_index(adjacency_matrix)
                data['edge_index'] = self.edge_index
                print(f"加载边索引: {self.edge_index.shape}")
            else:
                raise ValueError("未能找到邻接矩阵文件")
            
            # 加载聚类系数
            network_stats_path = os.path.join(self.data_dir, 'statistics_report.json')
            if os.path.exists(network_stats_path):
                with open(network_stats_path, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    if 'clustering_coefficients' in stats:
                        self.clustering_coef = np.array(stats['clustering_coefficients']).reshape(-1, 1)
                        data['clustering_coef'] = self.clustering_coef
                        print(f"加载聚类系数: {self.clustering_coef.shape}")
            
            # 加载网络完整数据（如果有）
            network_path = os.path.join(self.data_dir, 'network_complete.json')
            if os.path.exists(network_path):
                with open(network_path, 'r', encoding='utf-8') as f:
                    network_data = json.load(f)
                    data['network_data'] = network_data
            
            return data
            
        except Exception as e:
            print(f"数据加载失败: {e}")
            raise
    
    def _adjacency_to_edge_index(self, adjacency_matrix: np.ndarray) -> np.ndarray:
        """将邻接矩阵转换为边索引"""
        rows, cols = np.where(adjacency_matrix > 0)
        edge_index = np.vstack([rows, cols])
        return edge_index
    
    def prepare_pyg_data(self, features: np.ndarray, edge_index: np.ndarray, 
                         clustering_coef: Optional[np.ndarray] = None,
                         train_val_split: float = 0.8, random_state: int = 42) -> Data:
        """
        准备PyTorch Geometric数据对象
        
        Args:
            features: 节点特征
            edge_index: 边索引
            clustering_coef: 局部聚类系数
            train_val_split: 训练验证分割比例
            random_state: 随机种子
            
        Returns:
            PyG Data对象
        """
        # 标准化特征
        features_normalized = self.scaler.fit_transform(features)
        
        # 转换为PyTorch张量
        features_tensor = torch.FloatTensor(features_normalized)
        edge_index_tensor = torch.LongTensor(edge_index)
        
        # 创建PyG Data对象
        data = Data(x=features_tensor, edge_index=edge_index_tensor)
        
        # 添加聚类系数（如果可用）
        if clustering_coef is not None:
            data.clustering_coef = torch.FloatTensor(clustering_coef)
        
        # 划分训练集和验证集（节点索引）
        num_nodes = features.shape[0]
        indices = np.arange(num_nodes)
        train_indices, val_indices = train_test_split(
            indices, test_size=1-train_val_split, random_state=random_state
        )
        
        # 创建掩码
        train_mask = torch.zeros(num_nodes, dtype=torch.bool)
        val_mask = torch.zeros(num_nodes, dtype=torch.bool)
        train_mask[train_indices] = True
        val_mask[val_indices] = True
        
        data.train_mask = train_mask
        data.val_mask = val_mask
        
        return data
    
    def prepare_batch_data(self, batch_size: int = 32) -> list:
        """
        准备批次数据（用于大规模图）
        
        Args:
            batch_size: 批次大小
            
        Returns:
            批次数据列表
        """
        if self.node_features is None or self.edge_index is None:
            self.load_data()
        
        data = self.prepare_pyg_data(
            self.node_features, 
            self.edge_index, 
            self.clustering_coef
        )
        
        # 将大图拆分为多个子图（简化实现）
        num_nodes = data.x.size(0)
        batches = []
        
        for i in range(0, num_nodes, batch_size):
            end_idx = min(i + batch_size, num_nodes)
            
            # 创建子图数据（实际应用中需要更复杂的子图采样）
            batch_data = Data(
                x=data.x[i:end_idx],
                edge_index=data.edge_index,
                train_mask=data.train_mask[i:end_idx] if hasattr(data, 'train_mask') else None,
                val_mask=data.val_mask[i:end_idx] if hasattr(data, 'val_mask') else None
            )
            
            if hasattr(data, 'clustering_coef'):
                batch_data.clustering_coef = data.clustering_coef[i:end_idx]
            
            batches.append(batch_data)
        
        return batches
    
    def save_processed_data(self, output_dir: str):
        """保存处理后的数据"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存标准化器
        import joblib
        joblib.dump(self.scaler, os.path.join(output_dir, 'scaler.pkl'))
        
        print(f"处理后的数据已保存到: {output_dir}")


# 数据加载工厂函数
def load_data_for_gat(data_dir: str = '../data/processed/') -> Tuple[Data, Dict]:
    """
    加载数据并准备GAT训练
    
    Returns:
        (pyg_data, metadata)
    """
    loader = GATDataLoader(data_dir)
    raw_data = loader.load_data()
    
    pyg_data = loader.prepare_pyg_data(
        raw_data['features'],
        raw_data['edge_index'],
        raw_data.get('clustering_coef')
    )
    
    return pyg_data, raw_data