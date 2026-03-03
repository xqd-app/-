"""
数据保存模块
"""
import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List

class DataSaver:
    """数据保存器"""
    
    def __init__(self):
        pass
    
    def save_nodes_csv(self, nodes: List[Dict], output_path: str):
        """保存节点数据为CSV"""
        nodes_df = pd.DataFrame(nodes)
        nodes_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 保存节点数据: {output_path}")
        return output_path
    
    def save_edges_csv(self, edges: List[Dict], output_path: str):
        """保存边数据为CSV"""
        edges_df = pd.DataFrame(edges)
        edges_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 保存边数据: {output_path}")
        return output_path
    
    def save_simplified_nodes(self, nodes: List[Dict], output_path: str):
        """保存简化节点数据"""
        simplified_nodes = []
        for node in nodes:
            simplified = {
                'id': node['id'],
                'name': node['name'],
                'gender': node['gender'],
                'class': node['class'],
                'friend_count': node['friend_count'],
                'influence_score': node['influence_score'],
                'total_score': node['total_score'],
                'position': node['position'],
                'dorm': node['dorm']
            }
            simplified_nodes.append(simplified)
        
        pd.DataFrame(simplified_nodes).to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 保存简化节点数据: {output_path}")
        return output_path
    
    def save_network_json(self, nodes: List[Dict], edges: List[Dict], output_path: str):
        """保存网络数据为JSON格式"""
        # 简化节点用于JSON
        simplified_nodes = []
        for node in nodes:
            simplified = {
                'id': node['id'],
                'name': node['name'],
                'gender': node['gender'],
                'class': node['class'],
                'friend_count': node['friend_count'],
                'influence_score': node['influence_score'],
                'total_score': node['total_score'],
                'position': node['position'],
                'dorm': node['dorm']
            }
            simplified_nodes.append(simplified)
        
        network_data = {
            'nodes': simplified_nodes,
            'edges': edges,
            'metadata': {
                'num_nodes': len(nodes),
                'num_edges': len(edges),
                'density': len(edges) / (len(nodes) * max(len(nodes)-1, 1)),
                'description': '班级社交网络完整数据'
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 保存网络数据: {output_path}")
        return output_path
    
    def save_adjacency_matrix(self, nodes: List[Dict], edges: List[Dict], output_path: str):
        """保存邻接矩阵"""
        n = len(nodes)
        adj_matrix = np.zeros((n, n))
        
        for edge in edges:
            s, t = edge['source'], edge['target']
            if s < n and t < n:
                adj_matrix[s][t] = edge['weight']
        
        np.save(output_path, adj_matrix)
        print(f"✅ 保存邻接矩阵: {output_path}")
        return output_path
    
    def save_node_features(self, nodes: List[Dict], output_path: str):
        """保存节点特征矩阵"""
        # 更新特征列为9维
        feature_cols = [
            'social_norm', 'score_norm', 'leader_norm', 
            'learning_impact_norm', 'communication_ability_norm',
            'team_contribution_norm', 'friend_count',
            'age_norm', 'gender_encoded'  # 新增的两个特征
        ]
        
        # 检查哪些特征存在
        available_features = []
        for col in feature_cols:
            if col in nodes[0]:
                available_features.append(col)
        
        if available_features:
            features_df = pd.DataFrame(nodes)[available_features]
            features_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✅ 保存节点特征矩阵: {output_path}")
            
            # 同时保存为npy格式
            np.save(output_path.replace('.csv', '.npy'), features_df.values)
            print(f"✅ 保存节点特征矩阵(NPY): {output_path.replace('.csv', '.npy')}")
            
            return output_path
        else:
            print("⚠️  没有可用的特征列")
            return None
    
    def save_all_data(self, nodes: List[Dict], edges: List[Dict], output_dir: str):
        """保存所有数据"""
        print("\n💾 保存所有数据...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = {}
        
        # 保存各种格式的数据
        saved_files['nodes_complete'] = self.save_nodes_csv(nodes, f'{output_dir}/nodes_complete.csv')
        saved_files['nodes_simple'] = self.save_simplified_nodes(nodes, f'{output_dir}/nodes_simple.csv')
        saved_files['edges'] = self.save_edges_csv(edges, f'{output_dir}/edges.csv')
        saved_files['network'] = self.save_network_json(nodes, edges, f'{output_dir}/network_complete.json')
        saved_files['adjacency'] = self.save_adjacency_matrix(nodes, edges, f'{output_dir}/adjacency_matrix.npy')
        
        features_path = self.save_node_features(nodes, f'{output_dir}/node_features.csv')
        if features_path:
            saved_files['features'] = features_path
        
        print(f"\n🎉 所有数据已保存到: {output_dir}")
        
        return saved_files