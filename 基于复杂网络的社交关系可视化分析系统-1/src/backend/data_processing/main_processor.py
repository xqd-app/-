"""
主处理器 - 协调所有模块
"""
import pandas as pd
from typing import Dict, List, Tuple
import os

# 导入各个模块
from .loaders import DataLoader
from .preprocess import DataPreprocessor
from .network_builder import NetworkBuilder
from .feature_engineer import FeatureEngineer
from .saver import DataSaver
from .analyzer import DataAnalyzer
from .dao import DataDAO

class CompleteQuestionnaireProcessor:
    """完整的问卷处理器"""
    
    def __init__(self, use_database: bool = False):
        self.loader = DataLoader()
        self.preprocessor = DataPreprocessor()
        self.network_builder = NetworkBuilder()
        self.feature_engineer = FeatureEngineer()
        self.saver = DataSaver()
        self.analyzer = DataAnalyzer()
        self.dao = DataDAO(use_database=use_database)
        
        self.original_df = None
        self.processed_df = None
        self.nodes = []
        self.edges = []
        self.saved_files = {}
    
    def process(self, input_file: str, output_dir: str = "data/processed") -> bool:
        """运行完整的处理流程"""
        print("🚀 开始问卷数据处理")
        print("="*60)
        
        try:
            # 1. 加载数据
            self.original_df = self.loader.load_data(input_file)
            
            # 2. 预处理
            self.processed_df = self.preprocessor.run_preprocessing(self.original_df)
            
            # 3. 构建网络
            self.nodes, self.edges = self.network_builder.build_network(self.processed_df)
            
            # 4. 特征工程
            self.nodes = self.feature_engineer.run_feature_engineering(self.nodes, self.edges)
            
            # 5. 生成报告
            stats = self.analyzer.generate_summary_report(self.nodes, self.edges)
            
            # 6. 保存数据
            if self.dao.use_database:
                # 使用数据库保存
                self.dao.save_nodes(self.nodes)
                self.dao.save_edges(self.edges)
                self.saved_files = {}  # 数据库存储不需要文件路径
            else:
                # 使用文件保存
                self.saved_files = self.saver.save_all_data(self.nodes, self.edges, output_dir)
            
            # 7. 保存统计报告
            self.save_statistics_report(stats, output_dir)
            
            print("\n" + "="*60)
            print("🎉 问卷数据处理完成！")
            print("="*60)
            if self.dao.use_database:
                print("💾 数据已保存到数据库")
            else:
                print("📁 生成的文件:")
                for key, path in self.saved_files.items():
                    print(f"  ✅ {key}: {os.path.basename(path)}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_statistics_report(self, stats: Dict, output_dir: str):
        """保存统计报告"""
        import json
        
        report_path = os.path.join(output_dir, 'statistics_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 保存统计报告: {report_path}")
        self.saved_files['statistics'] = report_path
    
    def get_network_data(self) -> Dict:
        """获取网络数据"""
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'num_nodes': len(self.nodes),
            'num_edges': len(self.edges)
        }
    
    def get_summary_stats(self) -> Dict:
        """获取摘要统计"""
        return self.analyzer.generate_summary_report(self.nodes, self.edges)