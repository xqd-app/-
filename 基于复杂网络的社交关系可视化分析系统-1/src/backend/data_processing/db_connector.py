#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接器
提供MySQL数据库连接功能
"""

import pymysql
import yaml
import os
from typing import Dict, List, Any

class DatabaseConnector:
    """数据库连接器类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化数据库连接器
        
        Args:
            config_path: 数据库配置文件路径
        """
        if config_path is None:
            # 默认配置文件路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            config_path = os.path.join(project_root, 'config', 'db_config.yaml')
        
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.connection = None
    
    def connect(self) -> bool:
        """
        建立数据库连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 获取配置参数并确保密码是字符串类型
            host = self.config['host']
            port = self.config['port']
            user = self.config['user']
            password = str(self.config['password']) if self.config['password'] is not None else ''
            database = self.config['database']
            charset = self.config['charset']
            
            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset=charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("✅ 数据库连接成功")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            print("🔒 数据库连接已断开")
    
    def create_tables(self):
        """创建核心数据表"""
        if not self.connection:
            print("❌ 请先建立数据库连接")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # 创建user_roles表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_roles (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        role_name VARCHAR(50) UNIQUE NOT NULL,
                        description TEXT,
                        permissions JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建users表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        email VARCHAR(100),
                        role_id INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (role_id) REFERENCES user_roles(id) ON DELETE RESTRICT
                    )
                """)
                
                # 创建datasets表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS datasets (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        file_path VARCHAR(255),
                        uploaded_by INT,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
                    )
                """)
                
                # 创建raw_survey_data表 - 优化以存储完整的问卷数据
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS raw_survey_data (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id INT NOT NULL,
                        related_student_id INT,
                        relationship_type VARCHAR(50),
                        interaction_frequency INT CHECK (interaction_frequency >= 0 AND interaction_frequency <= 10),
                        familiarity_level INT CHECK (familiarity_level >= 0 AND familiarity_level <= 10),
                        communication_frequency INT CHECK (communication_frequency >= 0 AND communication_frequency <= 10),
                        study_collaboration INT CHECK (study_collaboration >= 0 AND study_collaboration <= 10),
                        social_activity_participation INT CHECK (social_activity_participation >= 0 AND social_activity_participation <= 10),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_student_id (student_id),
                        INDEX idx_related_student (related_student_id)
                    )
                """)
                
                # 创建优化的student_nodes表 - 包含所有特征命名规范中的字段
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_nodes (
                        id INT PRIMARY KEY,
                        name VARCHAR(50) NOT NULL,
                        gender ENUM('男', '女'),
                        class_name VARCHAR(50),
                        social_norm DOUBLE CHECK (social_norm >= 0 AND social_norm <= 1),  -- 社交活跃度归一化值
                        score_norm DOUBLE CHECK (score_norm >= 0 AND score_norm <= 1),    -- 学业成绩归一化值
                        leader_norm DOUBLE CHECK (leader_norm >= 0 AND leader_norm <= 1),  -- 领导力归一化值
                        position_encoded INT CHECK (position_encoded IN (0, 1)),  -- 职务编码值（1为班委，0为普通学生）
                        dorm_encoded VARCHAR(20),  -- 宿舍编码值
                        social_frequency DOUBLE,
                        learning_impact DOUBLE,
                        acceptance DOUBLE,
                        activity_participation DOUBLE,
                        communication_ability_norm DOUBLE,  -- 沟通能力归一化值
                        team_contribution_norm DOUBLE,      -- 团队贡献归一化值
                        learning_impact_norm DOUBLE,        -- 学习影响归一化值
                        friend_count INT,
                        influence_score DOUBLE,
                        pagerank DOUBLE,
                        clustering_coefficient DOUBLE,
                        degree_centrality DOUBLE,
                        eigenvector_centrality DOUBLE,
                        betweenness_centrality DOUBLE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_class (class_name),
                        INDEX idx_influence (influence_score),
                        INDEX idx_social_norm (social_norm)
                    )
                """)
                
                # 创建优化的social_edges表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS social_edges (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        source_id INT NOT NULL,
                        target_id INT NOT NULL,
                        weight DOUBLE CHECK (weight >= 0 AND weight <= 1),
                        relation_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (source_id) REFERENCES student_nodes(id) ON DELETE CASCADE,
                        FOREIGN KEY (target_id) REFERENCES student_nodes(id) ON DELETE CASCADE,
                        INDEX idx_source (source_id),
                        INDEX idx_target (target_id),
                        UNIQUE KEY unique_edge (source_id, target_id)
                    )
                """)
                
                # 创建model_results表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS model_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        node_id INT NOT NULL,
                        embedding_vector JSON,
                        attention_weights JSON,
                        predicted_influence DOUBLE,
                        model_version VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (node_id) REFERENCES student_nodes(id) ON DELETE CASCADE,
                        INDEX idx_node_id (node_id)
                    )
                """)
                
                # 创建propagation_records表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS propagation_records (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        simulation_id VARCHAR(50) NOT NULL,
                        iteration INT,
                        activated_nodes JSON,
                        spread_count INT,
                        model_type VARCHAR(20),
                        parameters JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_simulation (simulation_id)
                    )
                """)
                
                # 创建user_dataset_permissions表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_dataset_permissions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        dataset_id INT NOT NULL,
                        permission_level ENUM('read', 'write', 'admin') NOT NULL,
                        granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
                    )
                """)
                
                # 创建system_logs表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        action VARCHAR(100) NOT NULL,
                        details TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                        INDEX idx_user_timestamp (user_id, timestamp)
                    )
                """)
            
            self.connection.commit()
            print("✅ 数据表创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 数据表创建失败: {e}")
            self.connection.rollback()
            return False
    
    def insert_nodes(self, nodes: List[Dict]) -> bool:
        """
        插入节点数据
        
        Args:
            nodes: 节点数据列表
            
        Returns:
            bool: 插入是否成功
        """
        if not self.connection:
            print("❌ 请先建立数据库连接")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                for node in nodes:
                    cursor.execute("""
                        INSERT INTO student_nodes (
                            id, name, gender, class_name, social_norm, score_norm,
                            leader_norm, position_encoded, dorm_encoded, social_frequency, learning_impact,
                            acceptance, activity_participation, communication_ability_norm, team_contribution_norm,
                            learning_impact_norm, friend_count, influence_score,
                            pagerank, clustering_coefficient, degree_centrality, 
                            eigenvector_centrality, betweenness_centrality
                        ) VALUES (
                            %(id)s, %(name)s, %(gender)s, %(class_name)s, %(social_norm)s, %(score_norm)s,
                            %(leader_norm)s, %(position_encoded)s, %(dorm_encoded)s, %(social_frequency)s, %(learning_impact)s,
                            %(acceptance)s, %(activity_participation)s, %(communication_ability_norm)s, %(team_contribution_norm)s,
                            %(learning_impact_norm)s, %(friend_count)s, %(influence_score)s,
                            %(pagerank)s, %(clustering_coefficient)s, %(degree_centrality)s,
                            %(eigenvector_centrality)s, %(betweenness_centrality)s
                        ) ON DUPLICATE KEY UPDATE
                            name=VALUES(name), gender=VALUES(gender), class_name=VALUES(class_name),
                            social_norm=VALUES(social_norm), score_norm=VALUES(score_norm),
                            leader_norm=VALUES(leader_norm), position_encoded=VALUES(position_encoded), dorm_encoded=VALUES(dorm_encoded),
                            social_frequency=VALUES(social_frequency), learning_impact=VALUES(learning_impact),
                            acceptance=VALUES(acceptance), activity_participation=VALUES(activity_participation),
                            communication_ability_norm=VALUES(communication_ability_norm), team_contribution_norm=VALUES(team_contribution_norm),
                            learning_impact_norm=VALUES(learning_impact_norm),
                            friend_count=VALUES(friend_count), influence_score=VALUES(influence_score),
                            pagerank=VALUES(pagerank), clustering_coefficient=VALUES(clustering_coefficient),
                            degree_centrality=VALUES(degree_centrality), 
                            eigenvector_centrality=VALUES(eigenvector_centrality), betweenness_centrality=VALUES(betweenness_centrality)
                    """, node)
            
            self.connection.commit()
            print(f"✅ 成功插入 {len(nodes)} 条节点数据")
            return True
            
        except Exception as e:
            print(f"❌ 节点数据插入失败: {e}")
            self.connection.rollback()
            return False
    
    def insert_edges(self, edges: List[Dict]) -> bool:
        """
        插入边数据
        
        Args:
            edges: 边数据列表
            
        Returns:
            bool: 插入是否成功
        """
        if not self.connection:
            print("❌ 请先建立数据库连接")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                for edge in edges:
                    cursor.execute("""
                        INSERT INTO social_edges (
                            source_id, target_id, weight, relation_type
                        ) VALUES (
                            %(source_id)s, %(target_id)s, %(weight)s, %(relation_type)s
                        ) ON DUPLICATE KEY UPDATE
                            weight=VALUES(weight), relation_type=VALUES(relation_type)
                    """, edge)
            
            self.connection.commit()
            print(f"✅ 成功插入 {len(edges)} 条边数据")
            return True
            
        except Exception as e:
            print(f"❌ 边数据插入失败: {e}")
            self.connection.rollback()
            return False