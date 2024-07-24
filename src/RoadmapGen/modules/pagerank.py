import networkx as nx
from typing import Dict
from tqdm import tqdm

class ranker:
    def pagerank_recommend(self, graph: nx.DiGraph) -> Dict[str, float]:
        pagerank = nx.pagerank(graph)
        pagerank = dict(sorted(pagerank.items(), key=lambda item: item[1], reverse = True))
        return pagerank
    
    def pagerank_graph(self, graph: nx.DiGraph, pagerank: Dict[str, float]) -> nx.DiGraph:
        for node in tqdm(graph.nodes ,desc = 'Ranking each nodes'):
            new_attrs = {node : {'pagerank': pagerank[node]}}
            old_attrs = graph.nodes[node]
            nx.set_node_attributes(graph, {**old_attrs, **new_attrs})
        return graph
    
    def get_page_rank(self, graph: nx.DiGraph) -> nx.digraph:
        pagerank_dict = self.pagerank_recommend(graph)
        graph = self.pagerank_graph(graph, pagerank_dict)
        return graph
