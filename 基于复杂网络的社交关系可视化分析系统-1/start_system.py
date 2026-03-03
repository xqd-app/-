#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统启动脚本
一键启动整个社交关系分析系统
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser

def start_backend():
    """启动后端服务"""
    print("🚀 正在启动后端服务...")
    backend_script = os.path.join("src", "backend", "api", "server.py")
    
    try:
        # 启动后端服务
        backend_process = subprocess.Popen([
            sys.executable, backend_script
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
           universal_newlines=True, encoding='utf-8')
        
        print("✅ 后端服务已启动")
        return backend_process
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("🌐 前端服务通过后端静态文件服务提供")
    print("   前端页面将在浏览器中自动打开...")
    return True

def open_browser():
    """延时打开浏览器"""
    time.sleep(3)  # 等待后端服务启动
    try:
        webbrowser.open("http://localhost:5000")
        print("🎯 浏览器已打开，请查看系统界面")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print("   请手动访问 http://localhost:5000")

def main():
    """主函数"""
    print("=" * 60)
    print("🎓 基于复杂网络的社交关系可视化分析系统")
    print("=" * 60)
    
    # 启动后端服务
    backend_process = start_backend()
    if not backend_process:
        print("❌ 系统启动失败")
        return
    
    # 启动前端服务
    start_frontend()
    
    # 在新线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\nℹ️  系统信息:")
    print("   - 后端API服务: http://localhost:5000")
    print("   - 前端界面: http://localhost:5000")
    print("   - API文档: http://localhost:5000/api/docs (如果可用)")
    print("\n💡 提示:")
    print("   - 请勿关闭此窗口，否则服务将停止")
    print("   - 按 Ctrl+C 可停止服务")
    print("=" * 60)
    
    try:
        # 等待后端进程
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        backend_process.terminate()
        print("✅ 服务已停止")
        sys.exit(0)

if __name__ == "__main__":
    main()