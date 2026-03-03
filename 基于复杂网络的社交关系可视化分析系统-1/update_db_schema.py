#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库结构更新脚本
用于更新现有数据库表结构以匹配优化设计
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.backend.data_processing.db_connector import DatabaseConnector

def update_db_schema():
    """更新数据库表结构"""
    print("=" * 60)
    print("数据库结构更新")
    print("=" * 60)
    
    try:
        # 1. 连接数据库
        print("\n🔍 连接数据库...")
        db_connector = DatabaseConnector()
        if db_connector.connect():
            print("✅ 数据库连接成功")
        else:
            print("❌ 数据库连接失败")
            return False
        
        # 2. 删除现有表（注意：这将清除所有现有数据）
        print("\n⚠️  删除现有表（此操作将清除所有数据）...")
        try:
            with db_connector.connection.cursor() as cursor:
                # 按依赖顺序逆序删除表
                tables_to_drop = [
                    'user_dataset_permissions',
                    'system_logs',
                    'model_results',
                    'propagation_records',
                    'social_edges',
                    'raw_survey_data',
                    'student_nodes',
                    'datasets',
                    'users',
                    'user_roles'
                ]
                
                for table in tables_to_drop:
                    try:
                        cursor.execute(f"DROP TABLE IF EXISTS {table}")
                        print(f"✅ 删除表 {table}")
                    except Exception as e:
                        print(f"⚠️  删除表 {table} 时出错: {e}")
            
            db_connector.connection.commit()
            print("✅ 所有表已删除")
        except Exception as e:
            print(f"❌ 删除表时出错: {e}")
            return False
        
        # 3. 重新创建表
        print("\n🔍 重新创建优化后的表结构...")
        if db_connector.create_tables():
            print("✅ 优化后的数据表创建成功")
        else:
            print("❌ 数据表创建失败")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 数据库结构更新完成!")
        print("💡 现在数据库已使用优化后的表结构")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ 数据库结构更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_db_schema()
    if not success:
        print("\n❌ 数据库结构更新未完成，请检查错误信息")
        sys.exit(1)
    else:
        print("\n✅ 数据库结构更新完成!")
        sys.exit(0)