# network_analysis.py

import networkx as nx

def calculate_degree_centrality(graph):
    return nx.degree_centrality(graph)

def calculate_closeness_centrality(graph):
    return nx.closeness_centrality(graph)

def calculate_betweenness_centrality(graph):
    return nx.betweenness_centrality(graph)

def analyze_graph(graph):
    centrality_measures = {
        'degree_centrality': calculate_degree_centrality(graph),
        'closeness_centrality': calculate_closeness_centrality(graph),
        'betweenness_centrality': calculate_betweenness_centrality(graph)
    }
    return centrality_measures

def load_graph_from_data(data):
    graph = nx.Graph()
    for edge in data:
        graph.add_edge(edge[0], edge[1])
    return graph

def main(data):
    graph = load_graph_from_data(data)
    analysis_results = analyze_graph(graph)
    return analysis_results

if __name__ == "__main__":
    sample_data = [(1, 2), (1, 3), (2, 4), (3, 4)]
    results = main(sample_data)
    print(results)