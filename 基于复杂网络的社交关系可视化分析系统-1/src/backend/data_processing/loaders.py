"""
数据加载模块
"""
import pandas as pd
import os

class DataLoader:
    """数据加载器类"""
    
    @staticmethod
    def load_excel(file_path: str) -> pd.DataFrame:
        """加载Excel文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        df = pd.read_excel(file_path)
        print(f"✅ 加载Excel数据: {len(df)} 行, {len(df.columns)} 列")
        return df
    
    @staticmethod
    def load_csv(file_path: str) -> pd.DataFrame:
        """加载CSV文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"✅ 加载CSV数据: {len(df)} 行, {len(df.columns)} 列")
        return df
    
    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """检测文件类型，扩展名缺失时尝试解析内容。"""
        _, ext = os.path.splitext(file_path.lower())
        if ext in ('.xlsx', '.xls'):
            return 'excel'
        elif ext == '.csv':
            return 'csv'
        # no recognizable extension, try to read heuristically
        try:
            pd.read_excel(file_path)
            return 'excel'
        except Exception:
            pass
        try:
            pd.read_csv(file_path, encoding='utf-8-sig')
            return 'csv'
        except Exception:
            pass
        raise ValueError(f"不支持的文件格式: {file_path}")
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """通用数据加载方法"""
        file_type = self.detect_file_type(file_path)
        
        if file_type == 'excel':
            return self.load_excel(file_path)
        elif file_type == 'csv':
            return self.load_csv(file_path)