from flask import Blueprint, jsonify

api = Blueprint('api', __name__)

@api.route('/api/data', methods=['GET'])
def get_data():
    # 这里可以调用控制器来获取数据
    return jsonify({"message": "数据获取成功"})

@api.route('/api/analysis', methods=['POST'])
def analyze_data():
    # 这里可以处理分析请求
    return jsonify({"message": "数据分析成功"})