#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据访问对象(DAO)
统一提供数据库和文件两种数据访问方式
"""

import pandas as pd
import json
import os
from typing import Dict, List, Any, Union
from .db_connector import DatabaseConnector

class DataDAO:
    """数据访问对象"""
    
    def __init__(self, use_database: bool = False, db_config_path: str = None):
        """
        初始化数据访问对象
        
        Args:
            use_database: 是否使用数据库
            db_config_path: 数据库配置文件路径
        """
        self.use_database = use_database
        self.db_connector = None
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.data_dir = os.path.join(self.project_root, 'data', 'processed')
        
        if use_database:
            self.db_connector = DatabaseConnector(db_config_path)
            self.db_connector.connect()
            self.db_connector.create_tables()
    
    def save_nodes(self, nodes: List[Dict]) -> bool:
        """
        保存节点数据
        
        Args:
            nodes: 节点数据列表
            
        Returns:
            bool: 保存是否成功
        """
        if self.use_database:
            return self.db_connector.insert_nodes(nodes)
        else:
            # 使用文件方式保存
            nodes_df = pd.DataFrame(nodes)
            nodes_path = os.path.join(self.data_dir, 'nodes_complete.csv')
            nodes_df.to_csv(nodes_path, index=False, encoding='utf-8')
            print(f"✅ 节点数据已保存到: {nodes_path}")
            return True
    
    def save_edges(self, edges: List[Dict]) -> bool:
        """
        保存边数据
        
        Args:
            edges: 边数据列表
            
        Returns:
            bool: 保存是否成功
        """
        if self.use_database:
            return self.db_connector.insert_edges(edges)
        else:
            # 使用文件方式保存
            edges_df = pd.DataFrame(edges)
            edges_path = os.path.join(self.data_dir, 'edges.csv')
            edges_df.to_csv(edges_path, index=False, encoding='utf-8')
            print(f"✅ 边数据已保存到: {edges_path}")
            return True
    
    def save_model_results(self, results: Dict) -> bool:
        """
        保存模型结果
        
        Args:
            results: 模型结果数据
            
        Returns:
            bool: 保存是否成功
        """
        if self.use_database:
            # TODO: 实现数据库保存模型结果
            print("⚠️  数据库保存模型结果功能待实现")
            return False
        else:
            # 使用文件方式保存
            results_path = os.path.join(self.data_dir, 'model_results.json')
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 模型结果已保存到: {results_path}")
            return True
    
    def save_propagation_record(self, record: Dict) -> bool:
        """
        保存传播记录
        
        Args:
            record: 传播记录数据
            
        Returns:
            bool: 保存是否成功
        """
        if self.use_database:
            # TODO: 实现数据库保存传播记录
            print("⚠️  数据库保存传播记录功能待实现")
            return False
        else:
            # 使用文件方式保存，追加到现有记录文件
            records_path = os.path.join(self.data_dir, 'propagation_records.json')
            records = []
            if os.path.exists(records_path):
                with open(records_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            
            records.append(record)
            with open(records_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            print(f"✅ 传播记录已保存到: {records_path}")
            return True
    
    def load_nodes(self) -> List[Dict]:
        """
        加载节点数据
        
        Returns:
            List[Dict]: 节点数据列表
        """
        if self.use_database:
            # TODO: 实现从数据库加载节点数据
            print("⚠️  数据库加载节点数据功能待实现")
            return []
        else:
            # 从文件加载
            nodes_path = os.path.join(self.data_dir, 'nodes_complete.csv')
            if os.path.exists(nodes_path):
                nodes_df = pd.read_csv(nodes_path, encoding='utf-8')
                return nodes_df.to_dict('records')
            else:
                print(f"❌ 节点数据文件不存在: {nodes_path}")
                return []
    
    def load_edges(self) -> List[Dict]:
        """
        加载边数据
        
        Returns:
            List[Dict]: 边数据列表
        """
        if self.use_database:
            # TODO: 实现从数据库加载边数据
            print("⚠️  数据库加载边数据功能待实现")
            return []
        else:
            # 从文件加载
            edges_path = os.path.join(self.data_dir, 'edges.csv')
            if os.path.exists(edges_path):
                edges_df = pd.read_csv(edges_path, encoding='utf-8')
                return edges_df.to_dict('records')
            else:
                print(f"❌ 边数据文件不存在: {edges_path}")
                return []
    
    def close(self):
        """关闭数据访问对象"""
        if self.use_database and self.db_connector:
            self.db_connector.disconnect()