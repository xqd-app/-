#!/usr/bin/env python
"""
运行数据处理流水线
"""
import sys
import os
import argparse

# 添加项目根目录到路径，确保可以导入src.backend
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir
src_dir = os.path.join(project_root, 'src')
# 经常要将src目录加入，也可加入项目根使`import src...`可用
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='社交网络数据预处理')
    parser.add_argument('--use-database', action='store_true', help='使用数据库存储数据')
    args = parser.parse_args()
    
    from src.backend.data_processing.main_processor import CompleteQuestionnaireProcessor
    from src.backend.data_processing.utils import DataUtils
    
    print("🚀 社交网络数据预处理流水线")
    print("="*60)
    
    # 项目根目录
    project_root = current_dir
    
    # 查找数据文件
    data_filename = '基于复杂网络的社交关系可视化分析系统的设计与实现数据处理过.xlsx'
    data_file = DataUtils.find_data_file(project_root, data_filename)
    
    if not data_file:
        print(f"❌ 找不到数据文件: {data_filename}")
        print("请将数据文件放在以下位置之一:")
        print(f"  1. {os.path.join(project_root, 'data')}")
        print(f"  2. {project_root}")
        return False
    
    print(f"📂 数据文件: {data_file}")
    
    # 输出目录
    output_dir = os.path.join(project_root, 'data', 'processed')
    DataUtils.ensure_directory(output_dir)
    
    # 运行处理器
    processor = CompleteQuestionnaireProcessor(use_database=args.use_database)
    success = processor.process(data_file, output_dir)
    
    if success:
        print("\n✅ 所有问卷问题已处理完成！")
        print("📊 数据已准备好用于:")
        print("  1. 社交网络可视化")
        print("  2. GAT模型训练")
        print("  3. 影响力分析")
        print("  4. 复杂网络研究")
    else:
        print("\n❌ 处理失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)