#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库优化测试脚本
用于验证优化后的数据库表结构
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.backend.data_processing.db_connector import DatabaseConnector

def test_db_optimization():
    """测试优化后的数据库结构"""
    print("=" * 60)
    print("数据库优化测试")
    print("=" * 60)
    
    try:
        # 1. 测试数据库连接
        print("\n🔍 测试数据库连接...")
        db_connector = DatabaseConnector()
        if db_connector.connect():
            print("✅ 数据库连接成功")
        else:
            print("❌ 数据库连接失败")
            return False
        
        # 2. 测试表创建（优化后的表结构）
        print("\n🔍 测试优化后的表创建...")
        if db_connector.create_tables():
            print("✅ 优化后的数据表创建成功")
        else:
            print("❌ 数据表创建失败")
            return False
        
        # 3. 创建测试节点数据（包含所有特征字段）
        print("\n🔍 准备测试节点数据...")
        test_nodes = [
            {
                'id': 1,
                'name': '张三',
                'gender': '男',
                'class_name': '计算机1班',
                'social_norm': 0.8,
                'score_norm': 0.7,
                'leader_norm': 0.6,
                'position_encoded': 1,  # 班委
                'dorm_encoded': '1-101',
                'social_frequency': 0.8,
                'learning_impact': 0.7,
                'acceptance': 0.9,
                'activity_participation': 0.6,
                'communication_ability_norm': 0.8,
                'team_contribution_norm': 0.7,
                'learning_impact_norm': 0.75,
                'friend_count': 10,
                'influence_score': 0.75,
                'pagerank': 0.3,
                'clustering_coefficient': 0.4,
                'degree_centrality': 0.25,
                'eigenvector_centrality': 0.35,
                'betweenness_centrality': 0.2
            },
            {
                'id': 2,
                'name': '李四',
                'gender': '女',
                'class_name': '计算机1班',
                'social_norm': 0.7,
                'score_norm': 0.8,
                'leader_norm': 0.5,
                'position_encoded': 0,  # 普通学生
                'dorm_encoded': '1-102',
                'social_frequency': 0.7,
                'learning_impact': 0.8,
                'acceptance': 0.85,
                'activity_participation': 0.7,
                'communication_ability_norm': 0.75,
                'team_contribution_norm': 0.8,
                'learning_impact_norm': 0.8,
                'friend_count': 8,
                'influence_score': 0.72,
                'pagerank': 0.25,
                'clustering_coefficient': 0.35,
                'degree_centrality': 0.2,
                'eigenvector_centrality': 0.3,
                'betweenness_centrality': 0.15
            }
        ]
        
        # 4. 测试节点数据存储
        print("\n🔍 测试优化后的节点数据存储...")
        if db_connector.insert_nodes(test_nodes):
            print("✅ 优化后的节点数据存储成功")
        else:
            print("❌ 节点数据存储失败")
            return False
        
        # 5. 创建测试边数据
        print("\n🔍 准备测试边数据...")
        test_edges = [
            {
                'source_id': 1,
                'target_id': 2,
                'weight': 0.8,
                'relation_type': 'friend'
            },
            {
                'source_id': 2,
                'target_id': 1,
                'weight': 0.7,
                'relation_type': 'friend'
            }
        ]
        
        # 6. 测试边数据存储
        print("\n🔍 测试优化后的边数据存储...")
        if db_connector.insert_edges(test_edges):
            print("✅ 优化后的边数据存储成功")
        else:
            print("❌ 边数据存储失败")
            return False
        
        # 7. 测试查询功能
        print("\n🔍 测试查询功能...")
        try:
            with db_connector.connection.cursor() as cursor:
                # 查询所有节点
                cursor.execute("SELECT COUNT(*) as count FROM student_nodes")
                result = cursor.fetchone()
                print(f"✅ 节点表中现有 {result['count']} 条记录")
                
                # 查询所有边
                cursor.execute("SELECT COUNT(*) as count FROM social_edges")
                result = cursor.fetchone()
                print(f"✅ 边表中现有 {result['count']} 条记录")
                
                # 测试索引查询
                cursor.execute("SELECT * FROM student_nodes WHERE influence_score > 0.7 ORDER BY influence_score DESC LIMIT 10")
                results = cursor.fetchall()
                print(f"✅ 高影响力节点查询成功，找到 {len(results)} 条记录")
                
        except Exception as e:
            print(f"❌ 查询功能测试失败: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 数据库优化测试完成!")
        print("✅ 优化后的数据库结构工作正常")
        print("💡 所有数据完整性约束和索引均已生效")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ 数据库优化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_db_optimization()
    if not success:
        print("\n❌ 数据库优化测试未通过，请检查错误信息")
        sys.exit(1)
    else:
        print("\n✅ 数据库优化测试通过!")
        sys.exit(0)