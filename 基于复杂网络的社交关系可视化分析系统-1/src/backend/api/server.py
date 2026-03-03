#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端API服务
提供RESTful API接口，连接前端和后端功能模块
"""

import os
import sys
import json
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import numpy as np
import pandas as pd
import networkx as nx
import torch

from src.backend.model.gat_model import EnhancedGAT
from src.backend.model.dataloader import GATDataLoader

app = Flask(__name__, static_folder="../../frontend/public")
CORS(app)  # 允许跨域请求

# 设置数据和模型路径
data_dir = os.path.join(project_root, "data", "processed")
model_path = os.path.join(project_root, "models", "gat_model.pth")

@app.route('/api/network/data')
def get_network_data():
    """获取网络数据用于可视化"""
    try:
        # 加载节点数据
        nodes_df = pd.read_csv(os.path.join(data_dir, "nodes_complete.csv"))
        
        # 加载边数据
        edges_df = pd.read_csv(os.path.join(data_dir, "edges.csv"))
        
        # 构造节点列表
        nodes = []
        for _, row in nodes_df.iterrows():
            nodes.append({
                'id': int(row['id']),
                'name': row['name'],
                'influence': float(row['influence_score']),
                'friends': int(row['friend_count']),
                'position': row['position']
            })
        
        # 构造边列表
        links = []
        for _, row in edges_df.iterrows():
            links.append({
                'source': int(row['source']),
                'target': int(row['target'])
            })
        
        return jsonify({
            'nodes': nodes,
            'links': links
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/top-influencers')
def get_top_influencers():
    """获取关键人物分析结果"""
    try:
        # 加载节点数据
        nodes_df = pd.read_csv(os.path.join(data_dir, "nodes_complete.csv"))
        
        # 按影响力得分排序，选取Top 10
        top_nodes = nodes_df.nlargest(10, 'influence_score')
        
        influencers = []
        for _, row in top_nodes.iterrows():
            influencers.append({
                'id': int(row['id']),
                'name': row['name'],
                'influence_score': float(row['influence_score']),
                'friend_count': int(row['friend_count']),
                'total_score': float(row['total_score']),
                'position': row['position']
            })
        
        return jsonify(influencers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/network/metrics')
def get_network_metrics():
    """获取网络整体指标"""
    try:
        # 加载边数据构建网络
        edges_df = pd.read_csv(os.path.join(data_dir, "edges.csv"))
        
        # 创建网络图
        G = nx.DiGraph()
        for _, row in edges_df.iterrows():
            G.add_edge(int(row['source']), int(row['target']))
        
        # 计算网络指标
        metrics = {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'density': nx.density(G),
            'avg_clustering': nx.average_clustering(G.to_undirected()) if G.number_of_nodes() > 1 else 0,
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/path')
def find_path():
    """查找两名节点之间的最短路径（按姓名）"""
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()
    if not start or not end:
        return jsonify({'error': '起点或终点不能为空'}), 400
    try:
        nodes_df = pd.read_csv(os.path.join(data_dir, "nodes_complete.csv"))
        edges_df = pd.read_csv(os.path.join(data_dir, "edges.csv"))
        # map name to id
        name_to_id = dict(zip(nodes_df['name'], nodes_df['id']))
        if start not in name_to_id or end not in name_to_id:
            return jsonify({'path': None}), 200
        s_id = int(name_to_id[start])
        e_id = int(name_to_id[end])
        # build graph
        G = nx.DiGraph()
        for _, row in edges_df.iterrows():
            G.add_edge(int(row['source']), int(row['target']))
        if not nx.has_path(G, s_id, e_id):
            return jsonify({'path': None}), 200
        id_path = nx.shortest_path(G, s_id, e_id)
        # convert back to names preserving order
        id_to_name = dict(zip(nodes_df['id'], nodes_df['name']))
        name_path = [id_to_name.get(i, str(i)) for i in id_path]
        return jsonify({'path': name_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report')
def get_analysis_report():
    """获取综合分析报告"""
    try:
        report_path = os.path.join(data_dir, "statistics_report.json")
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            return jsonify(report)
        else:
            return jsonify({'error': '报告文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 提供静态文件服务
@app.route('/')
def index():
    """主页"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """静态文件服务"""
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)