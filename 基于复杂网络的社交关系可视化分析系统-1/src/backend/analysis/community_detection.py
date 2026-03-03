# community_detection.py

import networkx as nx

def detect_communities(graph):
    """
    使用Louvain算法检测图中的社区结构。
    
    参数:
    graph (networkx.Graph): 输入的图对象。
    
    返回:
    list: 检测到的社区列表，每个社区是一个节点列表。
    """
    import community as community_louvain

    partition = community_louvain.best_partition(graph)
    communities = {}
    
    for node, community_id in partition.items():
        if community_id not in communities:
            communities[community_id] = []
        communities[community_id].append(node)
    
    return list(communities.values())

def main():
    # 示例：创建一个图并检测社区
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5), (1, 5), (6, 7), (7, 8), (8, 6)])
    
    communities = detect_communities(G)
    print("检测到的社区:", communities)

if __name__ == "__main__":
    main()