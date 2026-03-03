"""
模型评估指标模块
"""
import torch
import torch.nn.functional as F
import numpy as np
from sklearn.metrics import pairwise_distances
from typing import Dict, Tuple


class GATMetrics:
    """GAT模型评估指标计算器"""
    
    @staticmethod
    def reconstruction_mae(original: torch.Tensor, reconstructed: torch.Tensor, 
                          mask: torch.Tensor = None) -> float:
        """计算重构平均绝对误差"""
        if mask is not None:
            mae = F.l1_loss(reconstructed[mask], original[mask], reduction='mean')
        else:
            mae = F.l1_loss(reconstructed, original, reduction='mean')
        return mae.item()
    
    @staticmethod
    def reconstruction_mse(original: torch.Tensor, reconstructed: torch.Tensor,
                          mask: torch.Tensor = None) -> float:
        """计算重构均方误差"""
        if mask is not None:
            mse = F.mse_loss(reconstructed[mask], original[mask], reduction='mean')
        else:
            mse = F.mse_loss(reconstructed, original, reduction='mean')
        return mse.item()
    
    @staticmethod
    def embedding_similarity(embeddings: torch.Tensor, top_k: int = 10) -> Dict:
        """计算嵌入相似度统计"""
        embeddings_np = embeddings.cpu().detach().numpy()
        
        # 计算余弦相似度
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(embeddings_np)
        
        # 对角线置零（自身相似度）
        np.fill_diagonal(similarity_matrix, 0)
        
        # 统计信息
        avg_similarity = np.mean(similarity_matrix)
        max_similarity = np.max(similarity_matrix)
        min_similarity = np.min(similarity_matrix)
        
        # 获取每个节点的top-k相似节点
        top_k_indices = np.argsort(similarity_matrix, axis=1)[:, -top_k:]
        top_k_values = np.take_along_axis(similarity_matrix, top_k_indices, axis=1)
        
        return {
            'avg_similarity': avg_similarity,
            'max_similarity': max_similarity,
            'min_similarity': min_similarity,
            'top_k_similarities': np.mean(top_k_values),
            'similarity_matrix': similarity_matrix
        }
    
    @staticmethod
    def clustering_coherence(embeddings: torch.Tensor, labels: np.ndarray = None) -> Dict:
        """
        计算嵌入的聚类一致性
        
        Args:
            embeddings: 节点嵌入
            labels: 真实标签（如果有）
            
        Returns:
            聚类一致性指标
        """
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score, calinski_harabasz_score
        
        embeddings_np = embeddings.cpu().detach().numpy()
        
        if labels is not None and len(np.unique(labels)) > 1:
            # 使用真实标签评估
            silhouette = silhouette_score(embeddings_np, labels)
            calinski = calinski_harabasz_score(embeddings_np, labels)
            
            return {
                'silhouette_score': silhouette,
                'calinski_harabasz_score': calinski,
                'clustering_method': 'ground_truth'
            }
        else:
            # 使用K-means聚类
            n_clusters = min(10, len(embeddings_np) // 10)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings_np)
            
            silhouette = silhouette_score(embeddings_np, cluster_labels)
            calinski = calinski_harabasz_score(embeddings_np, cluster_labels)
            
            return {
                'silhouette_score': silhouette,
                'calinski_harabasz_score': calinski,
                'cluster_labels': cluster_labels,
                'n_clusters': n_clusters,
                'clustering_method': 'kmeans'
            }
    
    @staticmethod
    def compute_all_metrics(original: torch.Tensor, reconstructed: torch.Tensor,
                           embeddings: torch.Tensor, mask: torch.Tensor = None,
                           labels: np.ndarray = None) -> Dict:
        """计算所有评估指标"""
        metrics = {}
        
        # 重构误差
        metrics['reconstruction_mae'] = GATMetrics.reconstruction_mae(original, reconstructed, mask)
        metrics['reconstruction_mse'] = GATMetrics.reconstruction_mse(original, reconstructed, mask)
        
        # 嵌入相似度
        similarity_metrics = GATMetrics.embedding_similarity(embeddings)
        metrics.update(similarity_metrics)
        
        # 聚类一致性
        clustering_metrics = GATMetrics.clustering_coherence(embeddings, labels)
        metrics.update(clustering_metrics)
        
        return metrics


class EarlyStopping:
    """早停机制"""
    
    def __init__(self, patience: int = 10, delta: float = 0):
        self.patience = patience
        self.delta = delta
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        
    def __call__(self, val_loss: float) -> bool:
        score = -val_loss
        
        if self.best_score is None:
            self.best_score = score
        elif score < self.best_score + self.delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.counter = 0
            
        return self.early_stop