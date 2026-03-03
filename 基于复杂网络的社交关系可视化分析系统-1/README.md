# 基于复杂网络的社交关系可视化分析系统

本项目是一个基于复杂网络和图神经网络（GAT）的社交关系分析与可视化系统，旨在分析班级内部的社交网络结构，识别关键人物，并提供直观的可视化展示。

## 📋 项目概述

本系统利用图注意力网络（GAT）对班级社交关系进行建模和分析，通过对学生间的互动关系、个人属性等多维度数据进行处理，挖掘社交网络中的关键节点，为班级管理和学生工作提供数据支持。

## 🎯 主要功能

1. **数据预处理** - 从问卷数据中提取社交关系和节点特征
2. **图神经网络建模** - 使用GAT模型学习节点表示
3. **影响力分析** - 识别社交网络中的关键人物
4. **可视化展示** - 提供直观的网络结构图和分析结果展示
5. **综合报告** - 生成详细的分析报告

## 📁 项目结构

```
├── data/                   # 数据目录
│   └── processed/          # 处理后的数据
├── models/                 # 训练好的模型
├── scripts/                # 数据处理和分析脚本
├── src/                    # 源代码
│   ├── backend/            # 后端服务
│   └── frontend/           # 前端界面
├── results/                # 分析结果和可视化图表
├── docs/                   # 文档资料
└── tests/                  # 测试代码
```

## 🔧 环境配置

### 系统要求
- Python 3.8+
- Node.js 14+ (前端开发)
- MySQL 5.7+ (用于持久化存储)
- Windows/Linux/macOS

### 安装依赖
```bash
# 安装Python依赖包
pip install -r requirements.txt

# 安装前端依赖包
cd src/frontend
npm install
cd ../../
```

### 数据库配置
在运行系统之前，请确保完成以下数据库配置：

1. **启动MySQL服务**
   确保MySQL数据库服务正在运行。可以通过以下命令检查：
   ```bash
   # Linux/Mac
   sudo systemctl status mysql
   # 或
   brew services list | grep mysql
   ```

2. **创建数据库**
   登录MySQL并创建专用数据库：
   ```sql
   CREATE DATABASE social_network_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **创建数据库用户（推荐）**
   为项目创建专用数据库用户：
   ```sql
   CREATE USER 'sns_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON social_network_analysis.* TO 'sns_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. **配置数据库连接**
   修改配置文件 `config/db_config.yaml`：
   ```yaml
   host: localhost
   port: 3306
   user: sns_user                    # 数据库用户名
   password: your_secure_password    # 数据库密码
   database: social_network_analysis # 数据库名称
   charset: utf8mb4
   connection_timeout: 30
   autocommit: true
   ```

5. **初始化数据库表结构**
   运行数据库初始化脚本：
   ```bash
   python scripts/init_database.py
   ```

6. **验证数据库连接**
   使用测试脚本验证配置是否正确：
   ```bash
   python scripts/test_db_connection.py
   ```

## ▶️ 系统启动

### 方法一：一键启动（推荐）
```bash
python start_system.py
```

这将自动启动后端服务并在浏览器中打开前端界面。

### 方法二：分别启动前后端

1. 启动后端服务：
```bash
python src/backend/api/server.py
```

2. 访问前端界面：
打开浏览器访问 `http://localhost:5000`

## 🚀 使用流程

1. **数据预处理**
```bash
# 使用文件存储（默认）
python scripts/run_preprocess.py

# 使用数据库存储（需要先配置数据库）
python scripts/run_preprocess.py --use-database
```

2. **模型训练**
```bash
python scripts/improved_train.py
```

3. **结果可视化**
```bash
python scripts/enhanced_visualization.py
```

## 📊 功能模块详解

### 1. 数据预处理模块
- 读取原始问卷数据
- 构建社交网络图结构
- 提取节点特征（社交活跃度、学业成绩、领导力等）
- 生成邻接矩阵和特征矩阵
- 支持文件存储和数据库存储两种方式

### 2. GAT模型训练模块
- 使用图注意力网络学习节点表示
- 通过特征重构任务优化模型参数
- 保存训练好的模型供后续分析使用

### 3. 可视化分析模块
- 生成社交网络结构图
- 分析关键人物及其影响力
- 对比不同影响力计算方法
- 生成综合分析报告

### 4. Web界面模块
- 基于HTML/CSS/JavaScript的前端界面
- RESTful API后端服务
- 实时交互式网络可视化
- 分析结果展示

## 📈 技术特点

1. **先进的图神经网络** - 使用GAT模型捕捉节点间复杂关系
2. **多维度特征融合** - 综合考虑社交、学业、个人特质等多个维度
3. **可视化分析** - 提供直观的网络结构图和分析结果展示
4. **可扩展性强** - 模块化设计，便于功能扩展和定制

## 📝 使用说明

1. 确保已安装所有依赖包
2. 准备好原始问卷数据文件
3. 运行数据预处理脚本生成网络数据
4. 训练GAT模型学习节点表示
5. 运行可视化脚本生成分析图表
6. 启动Web系统查看交互式分析结果

## 📚 相关文档

- [技术文档](docs/technical_documentation.md)
- [用户手册](docs/user_manual.md)
- [API文档](docs/api_documentation.md)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进本项目。

## 📄 许可证

本项目采用MIT许可证，详情请见[LICENSE](LICENSE)文件。

## 📞 联系方式

如有任何问题，请联系项目维护者。