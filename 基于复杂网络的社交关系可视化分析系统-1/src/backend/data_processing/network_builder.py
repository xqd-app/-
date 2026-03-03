"""
社交网络构建模块
"""
import re
from typing import Dict, List, Tuple
import pandas as pd

class NetworkBuilder:
    """社交网络构建器"""
    
    def __init__(self):
        self.name_to_id = {}
        self.student_nodes = []
        self.friend_edges = []
    
    def extract_chinese_names(self, text: str) -> List[str]:
        """从文本中提取中文姓名"""
        if pd.isna(text) or text == '未知':
            return []
        
        # 提取2-3个字符的中文名字
        names = re.findall(r'[\u4e00-\u9fff]{2,3}', str(text))
        return list(set(names))  # 去重
    
    def parse_social_frequency(self, value) -> float:
        """解析社交频率（1-5分）"""
        if isinstance(value, (int, float)):
            return float(value)
        
        text = str(value).strip()
        # 尝试从文本中提取数字
        numbers = re.findall(r'[1-5]', text)
        if numbers:
            return float(numbers[0])
        return 3.0  # 默认值
    
    def parse_scale(self, value) -> float:
        """解析量表题（转换为1-5分）"""
        if isinstance(value, (int, float)):
            return min(5.0, max(1.0, float(value)))
        
        text = str(value).strip().lower()
        
        # 尝试匹配常见量表值
        if '非常' in text or '很高' in text or '总是' in text:
            return 5.0
        elif '比较' in text or '经常' in text or '较高' in text:
            return 4.0
        elif '一般' in text or '有时' in text or '中等' in text:
            return 3.0
        elif '很少' in text or '较低' in text:
            return 2.0
        elif '从不' in text or '很低' in text:
            return 1.0
        
        # 尝试提取数字
        numbers = re.findall(r'[1-5]', text)
        if numbers:
            return float(numbers[0])
        
        return 3.0  # 默认值
    
    def parse_multi_choice(self, value) -> List[str]:
        """解析多选题"""
        if pd.isna(value):
            return []
        
        text = str(value).strip()
        # 按常见分隔符分割
        items = re.split(r'[;,，、\s]+', text)
        return [item.strip() for item in items if item.strip()]
    
    def build_network(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """构建社交网络"""
        print("\n🔗 构建社交网络...")
        
        nodes = []
        edges = []
        
        # 创建所有学生节点
        for idx, row in df.iterrows():
            student_id = idx
            name = str(row.get('name', f'学生{idx+1}')).strip()
            
            # 构建完整的学生节点
            node = {
                'id': student_id,
                'name': name,
                'gender': str(row.get('性别', '未知')).strip(),
                'class': str(row.get('班级', '未知')).strip(),
                'social_frequency': self.parse_social_frequency(row.get('您在班级中的社交互动频率如何?', '未知')),
                'interaction_types': self.parse_multi_choice(row.get('您在班级中最常与哪些类型的同学互动?（多选）', '')),
                'learning_impact': self.parse_scale(row.get('您认为班级中的社交关系对您的学习有怎样的影响?', '未知')),
                'acceptance': self.parse_scale(row.get('在班级中，您是否感觉被接纳和尊重?', '未知')),
                'classroom_interaction': self.parse_scale(row.get('在课堂上，您通常如何与同学交流互动?', '未知')),
                'activity_participation': self.parse_scale(row.get('您是否经常参加班级组织的活动或聚会?', '未知')),
                'communication_ability': self.parse_scale(row.get('你如何评估自己与他人的沟通和合作能力?', '未知')),
                'team_contribution': self.parse_scale(row.get('在团队项目中，你通常如何贡献自己的力量?', '未知')),
                'position': str(row.get('在班级、学院以及校级组织中担任的职务', '无')).strip(),
                'group_leader': float(row.get('在课上分组时担任小组长的情况', 0)),
                'personality': self.parse_multi_choice(row.get('你认为你符合以下哪种性格（多选）', '')),
                'influence_factors': str(row.get('你认为哪一方面对于个人在班级中的影响力影响最大', '未知')).strip(),
                'dorm': str(row.get('您的宿舍号是多少？', '未知')).strip(),
                'total_score': float(row.get('总分', 0)),
                'friend_count': 0,
                'influence_score': 0.0
            }
            nodes.append(node)
            
            # 保存姓名到ID的映射
            self.name_to_id[name] = student_id
        
        # 提取好友关系（第17题）
        friendship_col = '请您填写一下您本班的拥有的QQ和微信好友的真实姓（或者你能想起的本班同学的名字）'
        
        if friendship_col in df.columns:
            edge_count = 0
            for idx, row in df.iterrows():
                source_name = str(row.get('name', f'学生{idx+1}')).strip()
                source_id = idx
                
                friends_text = str(row[friendship_col])
                friend_names = self.extract_chinese_names(friends_text)
                
                for friend_name in friend_names:
                    if friend_name in self.name_to_id:
                        target_id = self.name_to_id[friend_name]
                        
                        # 避免自环
                        if source_id != target_id:
                            edge = {
                                'source': source_id,
                                'target': target_id,
                                'source_name': source_name,
                                'target_name': friend_name,
                                'weight': 1.0,
                                'type': 'friendship'
                            }
                            edges.append(edge)
                            edge_count += 1
            
            print(f"✅ 提取 {edge_count} 条好友关系")
        else:
            print("⚠️  未找到好友关系列")
        
        print(f"📊 网络构建完成: {len(nodes)} 个节点, {len(edges)} 条边")
        
        self.student_nodes = nodes
        self.friend_edges = edges
        
        return nodes, edges