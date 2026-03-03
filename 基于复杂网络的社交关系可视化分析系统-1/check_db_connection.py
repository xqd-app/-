#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.backend.data_processing.db_connector import DatabaseConnector

def test_database_connection():
    """测试数据库连接"""
    print("🔍 正在测试数据库连接...")
    
    try:
        # 创建数据库连接器
        db_connector = DatabaseConnector()
        
        # 尝试连接数据库
        if db_connector.connect():
            print("✅ 数据库连接成功!")
            
            # 测试创建表
            if db_connector.create_tables():
                print("✅ 数据表创建成功或已存在!")
            else:
                print("❌ 数据表创建失败!")
            
            # 断开连接
            db_connector.disconnect()
            return True
        else:
            print("❌ 数据库连接失败!")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("数据库连接测试")
    print("=" * 50)
    
    success = test_database_connection()
    
    print("=" * 50)
    if success:
        print("🎉 数据库连接测试通过!")
    else:
        print("💥 数据库连接测试失败!")
        print("\n请检查以下几点:")
        print("1. MySQL数据库是否已安装并正在运行")
        print("2. 数据库配置文件 config/db_config.yaml 是否正确")
        print("3. 是否已创建数据库 social_network_analysis")
        print("4. 用户名和密码是否正确")
    print("=" * 50)