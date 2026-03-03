"""
工具函数模块
"""
import os
import json
import numpy as np
from typing import List, Dict, Any

class DataUtils:
    """数据工具类"""
    
    @staticmethod
    def ensure_directory(path: str) -> str:
        """确保目录存在"""
        os.makedirs(path, exist_ok=True)
        return path
    
    @staticmethod
    def find_data_file(project_root: str, filename: str) -> str:
        """查找数据文件"""
        possible_paths = [
            os.path.join(project_root, 'data', filename),
            os.path.join(project_root, filename),
            os.path.join(os.path.dirname(project_root), filename)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @staticmethod
    def validate_network(nodes: List[Dict], edges: List[Dict]) -> bool:
        """验证网络数据的有效性"""
        if len(nodes) == 0:
            return False
        
        # 检查节点ID是否唯一
        node_ids = [node['id'] for node in nodes]
        if len(set(node_ids)) != len(node_ids):
            print("⚠️  警告: 节点ID不唯一")
            return False
        
        # 检查边是否有效
        valid_edge_count = 0
        for edge in edges:
            if edge['source'] < len(nodes) and edge['target'] < len(nodes):
                valid_edge_count += 1
        
        if valid_edge_count != len(edges):
            print(f"⚠️  警告: {len(edges) - valid_edge_count} 条边包含无效节点")
            return False
        
        return True
    
    @staticmethod
    def calculate_network_metrics(nodes: List[Dict], edges: List[Dict]) -> Dict:
        """计算网络指标"""
        n = len(nodes)
        m = len(edges)
        
        metrics = {
            'num_nodes': n,
            'num_edges': m,
            'density': m / (n * max(n-1, 1)),
            'avg_degree': m / n if n > 0 else 0,
            'directed': True  # 你的网络是有向的
        }
        
        return metrics
    
    @staticmethod
    def export_for_visualization(nodes: List[Dict], edges: List[Dict], output_path: str):
        """导出为可视化格式"""
        # 简化数据用于可视化
        simplified_nodes = []
        for node in nodes:
            simplified = {
                'id': node['id'],
                'label': node['name'],
                'group': node.get('gender', '未知'),
                'value': node.get('influence_score', 0),
                'title': f"姓名: {node['name']}<br>"
                        f"影响力: {node.get('influence_score', 0):.3f}<br>"
                        f"好友数: {node.get('friend_count', 0)}<br>"
                        f"成绩: {node.get('total_score', 0):.1f}<br>"
                        f"职务: {node.get('position', '无')}"
            }
            simplified_nodes.append(simplified)
        
        simplified_edges = []
        for edge in edges:
            simplified = {
                'from': edge['source'],
                'to': edge['target'],
                'value': edge.get('weight', 1.0)
            }
            simplified_edges.append(simplified)
        
        data = {
            'nodes': simplified_nodes,
            'edges': simplified_edges
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path