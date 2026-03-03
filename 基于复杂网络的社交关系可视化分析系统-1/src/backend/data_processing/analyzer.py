"""
数据分析模块
"""
import numpy as np
from collections import Counter
from typing import List, Dict

class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self):
        pass
    
    def generate_summary_report(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """生成摘要报告"""
        print("\n" + "="*60)
        print("📊 问卷数据分析报告")
        print("="*60)
        
        # 基本统计
        total_students = len(nodes)
        total_edges = len(edges)
        
        # 性别分布
        genders = [node['gender'] for node in nodes]
        gender_count = Counter(genders)
        
        # 好友数统计
        friend_counts = [node['friend_count'] for node in nodes]
        avg_friends = np.mean(friend_counts)
        max_friends = max(friend_counts)
        min_friends = min(friend_counts)
        
        # 成绩统计
        scores = [node['total_score'] for node in nodes]
        avg_score = np.mean(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        # 社交频率统计
        social_freqs = [node.get('social_frequency', 3) for node in nodes]
        avg_social_freq = np.mean(social_freqs)
        
        # 影响力统计
        influence_scores = [node['influence_score'] for node in nodes]
        avg_influence = np.mean(influence_scores)
        
        # 网络特性
        n = len(nodes)
        max_edges = n * (n - 1)
        density = total_edges / max_edges if max_edges > 0 else 0
        avg_degree = total_edges / n if n > 0 else 0
        
        # 宿舍分布
        dorms = [node['dorm'] for node in nodes]
        unique_dorms = set(dorms)
        
        # Top 10影响力学生
        sorted_nodes = sorted(nodes, key=lambda x: x['influence_score'], reverse=True)[:10]
        
        # 打印报告
        print(f"👥 学生总数: {total_students}")
        print(f"🔗 好友关系总数: {total_edges}")
        print(f"👨‍🎓 性别分布: {dict(gender_count)}")
        print(f"🤝 平均好友数: {avg_friends:.1f}")
        print(f"🤝 最多好友: {max_friends} (最少: {min_friends})")
        print(f"📚 平均成绩: {avg_score:.1f} (最高: {max_score:.1f}, 最低: {min_score:.1f})")
        print(f"💬 平均社交频率: {avg_social_freq:.1f}/5.0")
        print(f"🌟 平均影响力得分: {avg_influence:.3f}")
        
        print("\n🏆 影响力Top 10:")
        print("-" * 60)
        for i, node in enumerate(sorted_nodes, 1):
            print(f"{i:2d}. {node['name']:10s} | 影响力: {node['influence_score']:.3f} | "
                  f"好友: {node['friend_count']:2d} | 成绩: {node['total_score']:5.1f} | "
                  f"职务: {node['position']:10s}")
        
        print(f"\n🕸️  网络密度: {density:.3f}")
        print(f"📊 平均度: {avg_degree:.1f}")
        print(f"🏠 宿舍数: {len(unique_dorms)}")
        
        # 返回统计结果
        stats = {
            '学生总数': total_students,
            '好友关系总数': total_edges,
            '性别分布': dict(gender_count),
            '平均好友数': avg_friends,
            '最多好友': max_friends,
            '最少好友': min_friends,
            '平均成绩': avg_score,
            '最高成绩': max_score,
            '最低成绩': min_score,
            '平均社交频率': avg_social_freq,
            '平均影响力得分': avg_influence,
            '网络密度': density,
            '平均度': avg_degree,
            '宿舍数': len(unique_dorms),
            '影响力Top10': [
                {
                    '排名': i,
                    '姓名': node['name'],
                    '影响力': node['influence_score'],
                    '好友数': node['friend_count'],
                    '成绩': node['total_score'],
                    '职务': node['position']
                }
                for i, node in enumerate(sorted_nodes, 1)
            ]
        }
        
        return stats