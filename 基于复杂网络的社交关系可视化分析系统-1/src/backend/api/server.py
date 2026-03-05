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

from flask import Flask, jsonify, send_from_directory, request, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
import networkx as nx

# 有时依赖环境（如 NumPy 2.x 与 PyTorch 不兼容）会导致导入失败。
# 将模型相关模块放在 try/except 块内，以便服务器其余部分仍可启动。
try:
    import torch
    from src.backend.model.gat_model import EnhancedGAT
    from src.backend.model.dataloader import GATDataLoader
except Exception as _e:
    torch = None
    EnhancedGAT = None
    GATDataLoader = None
    print(f"⚠️ 模型模块导入失败: {_e}")

app = Flask(__name__, static_folder="../../frontend/public")
CORS(app)  # 允许跨域请求

# ensure numpy version is compatible with torch binaries
import numpy as _np

if _np.__version__.startswith("2"):
    # warn loudly during startup so developer can fix environment
    import warnings
    warnings.warn(
        "当前 NumPy 版本为 %s；与目前安装的 torch/torchvision 预编译模块不兼容，" \
        "请安装 numpy<2.0 或升级 torch。据 pip requirements.txt 所示。" % _np.__version__,
        UserWarning,
    )


# 设置数据和模型路径
data_dir = os.path.join(project_root, "data", "processed")
model_path = os.path.join(project_root, "models", "gat_model.pth")

# helper to attempt DB read
from src.backend.data_processing.dao import DataDAO

def _load_network(use_db: bool = False):
    # try database first if requested
    if use_db:
        try:
            dao = DataDAO(use_database=True)
            try:
                nodes = dao.load_nodes()
                edges = dao.load_edges()
            except Exception:
                nodes, edges = [], []
        except Exception as e:
            # failed to create DAO or connect
            print(f"_load_network 数据库访问失败: {e}")
            nodes, edges = [], []
        if nodes and edges:
            return nodes, edges
    # fallback to csv files; catch failures and return empty lists
    nodes, links = [], []
    try:
        nodes_df = pd.read_csv(os.path.join(data_dir, "nodes_complete.csv"))
        nodes = nodes_df.to_dict('records')
    except Exception:
        pass
    try:
        edges_df = pd.read_csv(os.path.join(data_dir, "edges.csv"))
        links = edges_df.to_dict('records')
    except Exception:
        pass
    return nodes, links

@app.route('/api/network/data')
def get_network_data():
    """获取网络数据用于可视化"""
    try:
        nodes, links = _load_network(use_db=True)
        # convert to expected format (field names may differ for db)
        def normalize_node(row):
            return {
                'id': int(row.get('id') or row.get('id')),
                'name': row.get('name'),
                'influence': float(row.get('influence_score', row.get('influence', 0))),
                'friends': int(row.get('friend_count', 0)),
                'position': row.get('position')
            }
        def normalize_link(row):
            # prefer explicit value, treat 0 as valid id
            s = row.get('source') if ('source' in row and row.get('source') is not None) else row.get('source_id')
            t = row.get('target') if ('target' in row and row.get('target') is not None) else row.get('target_id')
            try:
                s = int(s)
            except Exception:
                s = None
            try:
                t = int(t)
            except Exception:
                t = None
            return {'source': s, 'target': t}
        nodes_list = [normalize_node(r) for r in nodes]
        links_list = [normalize_link(r) for r in links]
        return jsonify({'nodes': nodes_list, 'links': links_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/top-influencers')
def get_top_influencers():
    """获取关键人物分析结果（按影响力得分排序，返回完整列表）"""
    try:
        nodes, _ = _load_network(use_db=True)
        # nodes already list of dicts
        df = pd.DataFrame(nodes)
        if df.empty:
            return jsonify([])
        # sort all nodes by influence_score descending
        df_sorted = df.sort_values('influence_score', ascending=False)
        influencers = []
        for _, row in df_sorted.iterrows():
            influencers.append({
                'id': int(row['id']),
                'name': row.get('name'),
                'influence_score': float(row.get('influence_score', 0)),
                'friend_count': int(row.get('friend_count', 0)),
                'total_score': float(row.get('total_score', 0)),
                'position': row.get('position')
            })
        return jsonify(influencers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _populate_graph_from_links(G: nx.DiGraph, links: list):
    """将链接列表安全地加入到图中，忽略缺失或无效的数据"""
    for row in links:
        # 可能存在source/target为None或丢失的情况
        s_raw = row.get('source') if ('source' in row and row.get('source') is not None) else row.get('source_id')
        t_raw = row.get('target') if ('target' in row and row.get('target') is not None) else row.get('target_id')
        try:
            src = int(s_raw)
            tgt = int(t_raw)
        except Exception:
            # 跳过无法转换为整数的关系
            continue
        G.add_edge(src, tgt)


@app.route('/api/network/metrics')
def get_network_metrics():
    """获取网络整体指标"""
    try:
        _, links = _load_network(use_db=True)
        G = nx.DiGraph()
        _populate_graph_from_links(G, links)
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
        nodes, links = _load_network(use_db=True)
        df_nodes = pd.DataFrame(nodes)
        name_to_id = dict(zip(df_nodes['name'], df_nodes['id']))
        if start not in name_to_id or end not in name_to_id:
            return jsonify({'path': None}), 200
        s_id = int(name_to_id[start])
        e_id = int(name_to_id[end])
        G = nx.DiGraph()
        _populate_graph_from_links(G, links)
        if not nx.has_path(G, s_id, e_id):
            return jsonify({'path': None}), 200
        id_path = nx.shortest_path(G, s_id, e_id)
        id_to_name = dict(zip(df_nodes['id'], df_nodes['name']))
        name_path = [id_to_name.get(i, str(i)) for i in id_path]
        return jsonify({'path': name_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report')
def get_analysis_report():
    """获取综合分析报告"""
    try:
        # first try DB summary (if present)
        dao = DataDAO(use_database=True)
        # assume processor saved a statistics_report file anyway
        report_path = os.path.join(data_dir, "statistics_report.json")
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            return jsonify(report)
        else:
            return jsonify({'error': '报告文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 上传接口
from werkzeug.utils import secure_filename

# --- 简单登录/会话配置 ---
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_this_secret')

UPLOAD_DIR = os.path.join(project_root, 'data', 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/api/login', methods=['POST'])
def login():
    """根据用户名/密码进行数据库验证并返回用户信息"""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'error': '用户名或密码不能为空'}), 400
    try:
        dao = DataDAO(use_database=True)
        user = dao.get_user_by_username(username)
        if not user:
            return jsonify({'error': '用户不存在'}), 401
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': '密码错误'}), 401
        # update last login
        dao.update_last_login(user['id'])
        # 简单会话存储
        session['user_id'] = user['id']
        session['username'] = username
        return jsonify({'status': 'ok', 'user': {'id': user['id'], 'username': username}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """创建新用户（主要用于初始化或测试）。注册后可立即登录。"""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    try:
        dao = DataDAO(use_database=True)
        # ensure a default role exists
        with dao.db_connector.connection.cursor() as cursor:
            cursor.execute("SELECT id FROM user_roles WHERE role_name=%s", ('user',))
            r = cursor.fetchone()
            if r is None:
                cursor.execute("INSERT INTO user_roles (role_name, description) VALUES (%s,%s)",
                               ('user', '普通用户'))
                role_id = cursor.lastrowid
            else:
                role_id = r['id']
            # check if username already exists
            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                return jsonify({'error': '用户名已被占用'}), 409
            pw_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role_id) VALUES (%s,%s,%s)",
                (username, pw_hash, role_id)
            )
            dao.db_connector.connection.commit()
        return jsonify({'status': 'created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """接收前端上传的Excel/CSV并运行预处理，结果写入数据库"""
    if 'file' not in request.files:
        return jsonify({'error': '未找到文件字段'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名不能为空'}), 400
    # ensure filename has extension, try to recover if missing
    original_name = file.filename or ''
    filename = secure_filename(original_name)
    if '.' not in filename:
        # attempt guess from content_type
        ct = file.content_type or ''
        if 'spreadsheetml' in ct or 'excel' in ct:
            filename += '.xlsx'
        elif 'csv' in ct:
            filename += '.csv'
        else:
            # fallback to .xlsx
            filename += '.xlsx'
    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    # 调用处理器，将use_database设为True
    try:
        from src.backend.data_processing.main_processor import CompleteQuestionnaireProcessor
        processor = CompleteQuestionnaireProcessor(use_database=True)
        processor.process(save_path, os.path.join(project_root, 'data', 'processed'))
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/list')
def list_uploaded_files():
    """返回uploads目录下的文件名列表"""
    try:
        files = []
        for fname in os.listdir(UPLOAD_DIR):
            if os.path.isfile(os.path.join(UPLOAD_DIR, fname)):
                files.append(fname)
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 提供静态文件服务
@app.route('/login')
def login_page():
    """登录界面"""
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/')
def index():
    """主页，要求已经登录。未登陆则重定向到 /login"""
    if not session.get('user_id'):
        return send_from_directory(app.static_folder, 'login.html')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """静态文件服务"""
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)