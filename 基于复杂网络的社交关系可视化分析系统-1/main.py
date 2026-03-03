#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于复杂网络的社交关系可视化分析系统主入口
整合数据预处理、模型训练和可视化分析全流程
"""

import os
import sys
import argparse
import subprocess

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def run_script(script_name, description):
    """
    运行指定脚本
    
    Args:
        script_name (str): 脚本文件名
        description (str): 脚本描述
    """
    script_path = os.path.join(project_root, 'scripts', script_name)
    print(f"🚀 正在运行{description}...")
    
    try:
        # 在Windows上使用shell=True并指定编码来避免UnicodeDecodeError
        result = subprocess.run([sys.executable, script_path], 
                              cwd=project_root,
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8',
                              shell=True if os.name == 'nt' else False)
        
        if result.returncode == 0:
            print(f"✅ {description}完成!")
            if result.stdout:
                # 只打印关键信息，避免输出过多
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:  # 只显示最后5行
                    if line.strip():
                        print(f"   {line}")
        else:
            print(f"❌ {description}失败!")
            print(f"   错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 运行{description}时出现异常: {e}")
        return False
        
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='基于复杂网络的社交关系可视化分析系统')
    parser.add_argument('--steps', nargs='+', 
                       choices=['preprocess', 'train', 'visualize', 'all'],
                       default=['all'],
                       help='选择要执行的步骤: preprocess(数据预处理), train(模型训练), visualize(可视化分析), all(全流程)')
    
    args = parser.parse_args()
    
    print("🎓 基于复杂网络的社交关系可视化分析系统")
    print("=" * 50)
    
    steps_to_run = args.steps
    if 'all' in steps_to_run:
        steps_to_run = ['preprocess', 'train', 'visualize']
    
    success = True
    
    # 执行数据预处理
    if 'preprocess' in steps_to_run:
        success &= run_script('run_preprocess.py', '数据预处理')
        print()
    
    # 执行模型训练
    if 'train' in steps_to_run:
        success &= run_script('improved_train.py', '模型训练')
        print()
    
    # 执行可视化分析
    if 'visualize' in steps_to_run:
        success &= run_script('enhanced_visualization.py', '可视化分析')
        print()
    
    # 输出最终结果
    if success:
        print("=" * 50)
        print("🎉 所有步骤执行成功!")
        print(f"📁 结果保存在: {os.path.join(project_root, 'results')}")
        print("📊 您可以查看生成的图表和报告了解分析结果")
    else:
        print("=" * 50)
        print("❌ 执行过程中出现错误，请检查日志信息")
        sys.exit(1)

if __name__ == "__main__":
    main()