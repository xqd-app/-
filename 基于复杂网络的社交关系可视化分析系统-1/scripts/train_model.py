"""
GAT模型训练使用示例
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.backend.model import (
    GATConfig,
    GATDataLoader,
    GATTrainer,
    set_random_seed
)

def main():
    """主函数示例"""
    # 1. 设置随机种子
    set_random_seed(42)
    
    # 2. 加载数据
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    print(f"当前工作目录: {os.getcwd()}")
    print(f"数据目录路径: {os.path.abspath(data_dir)}")
    
    loader = GATDataLoader(data_dir)
    raw_data = loader.load_data()
    
    print(f"加载的数据键: {list(raw_data.keys())}")
    
    # 检查是否成功加载了特征数据
    if 'features' not in raw_data:
        raise ValueError("未能加载节点特征数据，请检查数据文件是否存在")
    
    if 'edge_index' not in raw_data:
        raise ValueError("未能加载边索引数据，请检查邻接矩阵文件是否存在")
    
    print(f"特征形状: {raw_data['features'].shape}")
    print(f"边索引形状: {raw_data['edge_index'].shape}")
    
    # 3. 准备PyG数据
    pyg_data = loader.prepare_pyg_data(
        raw_data['features'],
        raw_data['edge_index'],
        raw_data.get('clustering_coef')
    )
    
    # 4. 创建配置（使用增强版配置）
    config = GATConfig(
        input_dim=pyg_data.x.shape[1],  # 现在应该是9维
        hidden_dims=[32],  # 简化隐藏层配置
        output_dim=64,
        heads=[4, 1],  # 简化注意力头配置
        dropout=0.6,
        learning_rate=0.001,
        weight_decay=5e-4,
        epochs=1500,  # 恢复到正常的1500轮训练
        batch_size=32,
        train_val_split=0.8,
        random_seed=42,
        # 早停机制参数
        early_stopping=True,
        patience=100,
        # 学习率调度参数
        scheduler_factor=0.5,
        scheduler_patience=50,
        # 梯度裁剪
        gradient_clip=1.0,
        # 日志记录
        log_interval=10
    )
    
    # 5. 创建训练器并训练
    trainer = GATTrainer(config)
    history = trainer.train(pyg_data)
    
    # 6. 获取节点嵌入
    embeddings = trainer.get_node_embeddings(pyg_data)
    print(f"生成的64维嵌入维度: {embeddings.shape}")
    
    # 7. 保存模型和嵌入
    trainer.save_model('../models/gat_model.pth')
    
    return embeddings

if __name__ == "__main__":
    embeddings = main()