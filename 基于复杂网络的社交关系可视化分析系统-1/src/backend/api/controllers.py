from flask import request, jsonify

# 使用异常处理确保在不同运行方式下都能正确导入
try:
    # 尝试使用相对导入（在包中正常工作）
    from ..analysis.network_analysis import perform_network_analysis
    from ..data_processing.loaders import load_data
except ImportError:
    # 当直接运行脚本时使用绝对导入
    from src.backend.analysis.network_analysis import perform_network_analysis
    from src.backend.data_processing.loaders import load_data

def analyze_network():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    analysis_result = perform_network_analysis(data)
    return jsonify(analysis_result), 200

def get_data():
    dataset = load_data()
    return jsonify(dataset), 200