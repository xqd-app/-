"""
特征工程模块
"""
import numpy as np
from typing import List, Dict

class FeatureEngineer:
    """特征工程师"""
    
    def __init__(self):
        pass
    
    def normalize_features(self, nodes: List[Dict]) -> List[Dict]:
        """归一化特征"""
        print("\n📊 归一化特征...")
        
        for node in nodes:
            # 归一化处理
            node['social_norm'] = node.get('social_frequency', 3.0) / 5.0
            node['score_norm'] = min(1.0, node.get('total_score', 0) / 100.0)
            node['leader_norm'] = min(1.0, node.get('group_leader', 0) / 10.0)
            
            # 各种能力的归一化（假设是1-5量表）
            for ability in ['learning_impact', 'acceptance', 'classroom_interaction', 
                          'activity_participation', 'communication_ability', 'team_contribution']:
                if ability in node:
                    node[f'{ability}_norm'] = node[ability] / 5.0
                    
            # 添加额外的两个特征以达到9维
            # 年龄归一化特征
            node['age_norm'] = max(0.0, min(1.0, (node.get('age', 20) - 15) / 10.0))
            
            # 性别编码特征（男性为1，女性为0）
            node['gender_encoded'] = 1.0 if node.get('gender', '男') == '男' else 0.0
        
        return nodes
    
    def calculate_friend_counts(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """计算好友数量"""
        print("计算好友数量...")
        
        # 计算每个节点的好友数
        friend_counts = {}
        for edge in edges:
            source = edge['source']
            friend_counts[source] = friend_counts.get(source, 0) + 1
        
        # 更新节点信息
        for node in nodes:
            node_id = node['id']
            node['friend_count'] = friend_counts.get(node_id, 0)
        
        return nodes
    
    def calculate_influence_score(self, nodes: List[Dict]) -> List[Dict]:
        """计算综合影响力得分"""
        print("计算综合影响力得分...")
        
        # 计算好友数归一化
        friend_counts = [node.get('friend_count', 0) for node in nodes]
        max_friends = max(friend_counts) if friend_counts else 1
        
        for node in nodes:
            influence_score = 0.0
            weights = 0.0
            
            # 社交活跃度权重 (0.2)
            influence_score += node.get('social_norm', 0) * 0.2
            weights += 0.2
            
            # 学业成绩权重 (0.15)
            influence_score += node.get('score_norm', 0) * 0.15
            weights += 0.15
            
            # 好友数权重 (0.15)
            friend_norm = node['friend_count'] / max_friends if max_friends > 0 else 0
            influence_score += friend_norm * 0.15
            weights += 0.15
            
            # 领导力权重 (0.2) - 增强班委重要性
            influence_score += node.get('leader_norm', 0) * 0.2
            weights += 0.2
            
            # 沟通合作能力权重 (0.1)
            if 'communication_ability_norm' in node:
                influence_score += node['communication_ability_norm'] * 0.1
                weights += 0.1
            
            # 团队贡献权重 (0.1)
            if 'team_contribution_norm' in node:
                influence_score += node['team_contribution_norm'] * 0.1
                weights += 0.1
            
            # 社交关系影响权重 (0.05)
            if 'learning_impact_norm' in node:
                influence_score += node['learning_impact_norm'] * 0.05
                weights += 0.05
            
            # 最终归一化
            if weights > 0:
                node['influence_score'] = influence_score / weights
            else:
                node['influence_score'] = 0.0
        
        return nodes
    
    def run_feature_engineering(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """运行完整的特征工程流程"""
        print("\n🔧 开始特征工程...")
        
        # 1. 计算好友数
        nodes = self.calculate_friend_counts(nodes, edges)
        
        # 2. 归一化特征
        nodes = self.normalize_features(nodes)
        
        # 3. 计算影响力得分
        nodes = self.calculate_influence_score(nodes)
        
        print("✅ 特征工程完成")
        
        return nodes