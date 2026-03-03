"""
模型工具函数模块
"""
import torch
import numpy as np
import json
import yaml
from typing import Dict, Any, Optional
import os


def set_random_seed(seed: int = 42):
    """设置随机种子"""
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def save_embeddings(embeddings: np.ndarray, node_ids: Optional[np.ndarray] = None,
                   output_path: str = '../data/processed/node_embeddings.npy'):
    """保存节点嵌入"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存嵌入矩阵
    np.save(output_path, embeddings)
    
    # 保存嵌入元数据
    metadata = {
        'num_nodes': embeddings.shape[0],
        'embedding_dim': embeddings.shape[1],
        'node_ids': node_ids.tolist() if node_ids is not None else []
    }
    
    metadata_path = output_path.replace('.npy', '_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"节点嵌入已保存到: {output_path}")
    print(f"嵌入元数据已保存到: {metadata_path}")
    
    return embeddings


def load_embeddings(embeddings_path: str) -> Dict[str, Any]:
    """加载节点嵌入"""
    embeddings = np.load(embeddings_path)
    
    metadata_path = embeddings_path.replace('.npy', '_metadata.json')
    metadata = {}
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    
    return {
        'embeddings': embeddings,
        'metadata': metadata
    }


def export_embeddings_for_viz(embeddings: np.ndarray, node_ids: np.ndarray,
                             output_path: str = '../data/processed/viz_embeddings.json'):
    """导出用于可视化的嵌入数据"""
    # 使用PCA或t-SNE降维到2D
    from sklearn.decomposition import PCA
    
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings)
    
    # 准备可视化数据
    viz_data = {
        'nodes': [],
        'embeddings_2d': embeddings_2d.tolist(),
        'embeddings_original': embeddings.tolist(),
        'pca_explained_variance': pca.explained_variance_ratio_.tolist()
    }
    
    for i, node_id in enumerate(node_ids):
        viz_data['nodes'].append({
            'id': str(node_id),
            'x': float(embeddings_2d[i, 0]),
            'y': float(embeddings_2d[i, 1]),
            'original_embedding': embeddings[i].tolist()
        })
    
    # 保存为JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(viz_data, f, indent=2, ensure_ascii=False)
    
    print(f"可视化嵌入数据已保存到: {output_path}")
    print(f"PCA解释方差: {pca.explained_variance_ratio_}")
    
    return viz_data


def compute_clustering_coefficient(adjacency_matrix: np.ndarray) -> np.ndarray:
    """计算局部聚类系数"""
    n = adjacency_matrix.shape[0]
    clustering_coef = np.zeros(n)
    
    for i in range(n):
        # 找到节点i的邻居
        neighbors = np.where(adjacency_matrix[i] > 0)[0]
        k = len(neighbors)
        
        if k < 2:
            clustering_coef[i] = 0.0
        else:
            # 计算邻居之间的边数
            neighbor_adj = adjacency_matrix[neighbors][:, neighbors]
            edges_between_neighbors = np.sum(neighbor_adj) / 2  # 除以2因为是无向图
            
            # 最大可能边数
            max_possible_edges = k * (k - 1) / 2
            
            clustering_coef[i] = edges_between_neighbors / max_possible_edges
    
    return clustering_coef


def prepare_config_from_data(data_features: np.ndarray) -> Dict[str, Any]:
    """根据数据特征准备配置"""
    input_dim = data_features.shape[1]
    
    # 根据输入维度自动调整隐藏层维度
    if input_dim >= 256:
        hidden_dims = [512, 256]
    elif input_dim >= 128:
        hidden_dims = [256, 128]
    else:
        hidden_dims = [128, 64]
    
    config = {
        'input_dim': input_dim,
        'hidden_dims': hidden_dims,
        'output_dim': 64,
        'heads': 8,
        'dropout': 0.6,
        'use_clustering_coef': True,
        'learning_rate': 0.001,
        'epochs': 200,
        'batch_size': 32,
        'train_val_split': 0.8,
        'random_seed': 42
    }
    
    return config