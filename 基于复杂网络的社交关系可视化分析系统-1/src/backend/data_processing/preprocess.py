"""
数据预处理主模块
"""
import pandas as pd
import re
from typing import Dict, List

class DataPreprocessor:
    """数据预处理器"""
    
    def __init__(self):
        self.original_columns = []
        self.cleaned_columns = []
        
    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """重命名列名（去掉序号）"""
        self.original_columns = list(df.columns)
        
        column_mapping = {}
        for col in df.columns:
            if isinstance(col, str) and '.' in col:
                # 去掉序号，保留问题文本
                new_col = col.split('.', 1)[1].strip()
                column_mapping[col] = new_col
            else:
                column_mapping[col] = str(col)
        
        df = df.rename(columns=column_mapping)
        self.cleaned_columns = list(df.columns)
        
        print(f"🔄 重命名列: {len(self.original_columns)} → {len(self.cleaned_columns)}")
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        print("处理缺失值...")
        
        # 定义文本列和数值列
        text_columns = [
            '性别', '班级', '您在班级中的社交互动频率如何?',
            '您在班级中最常与哪些类型的同学互动?（多选）',
            '您认为班级中的社交关系对您的学习有怎样的影响?',
            '在班级中，您是否感觉被接纳和尊重?',
            '在课堂上，您通常如何与同学交流互动?',
            '您是否经常参加班级组织的活动或聚会?',
            '在实践活动中，你通常扮演什么角色?',
            '你如何评估自己与他人的沟通和合作能力?',
            '在团队项目中，你通常如何贡献自己的力量?',
            '在班级、学院以及校级组织中担任的职务',
            '你认为你符合以下哪种性格（多选）',
            '你认为哪一方面对于个人在班级中的影响力影响最大',
            '请您填写一下您本班的拥有的QQ和微信好友的真实姓（或者你能想起的本班同学的名字）',
            '您的宿舍号是多少？'
        ]
        
        # 文本列用'未知'填充
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('未知')
        
        # 数值列用0填充
        if '总分' in df.columns:
            df['总分'] = pd.to_numeric(df['总分'], errors='coerce').fillna(0)
        if '在课上分组时担任小组长的情况' in df.columns:
            df['在课上分组时担任小组长的情况'] = pd.to_numeric(
                df['在课上分组时担任小组长的情况'], errors='coerce'
            ).fillna(0)
        
        # 确保姓名列存在
        if '姓名' in df.columns:
            df = df.rename(columns={'姓名': 'name'})
        elif 'name' not in df.columns:
            df['name'] = [f'学生{i+1}' for i in range(len(df))]
        
        return df
    
    def run_preprocessing(self, df: pd.DataFrame) -> pd.DataFrame:
        """运行完整的预处理流程"""
        print("\n🧹 开始数据预处理...")
        
        # 1. 重命名列
        df = self.rename_columns(df)
        
        # 2. 处理缺失值
        df = self.handle_missing_values(df)
        
        # 3. 打印处理结果
        print(f"✅ 预处理完成，数据形状: {df.shape}")
        print(f"📋 处理后列名: {list(df.columns)[:10]}...")
        
        return df