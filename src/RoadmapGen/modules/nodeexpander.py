from ..core.RoadmapGenerator import Generator
from .RedunRemover import RedundantFunc
from .websearch import ResourceFinder
from .pagerank import ranker
from .nodefixer import GraphFixer
from .pagerank import ranker
from .jsonranker import sortpgscore
from typing import Dict
import networkx as nx

class NodeExpand:
    def __init__(self, client, SERPER_API_KEY):
        self.client=client
        self.SERPER_API_KEY = SERPER_API_KEY

    def get_child_topic_desc(self, targetnode: str, graph: nx.DiGraph) -> str:
        try:
            for node, data in graph.nodes(data=True):
                if node == targetnode:
                    return data.get('title', '')
        except ValueError as e:
            print(f"Error: {e}")
        return ''

    def connect_expanded_graph(self, original_graph: nx.DiGraph, expanded_graph: nx.DiGraph, targetnode: str) -> nx.DiGraph:
        for node, data in expanded_graph.nodes(data=True):
            if node != targetnode:
                original_graph.add_node(node, **data)
                original_graph.add_edge(targetnode, node)

        for edge in expanded_graph.edges(data=True):
            original_graph.add_edge(edge[0], edge[1], **edge[2])

        return original_graph
    
    def delete_pagerank(self, graph: nx.DiGraph) -> nx.DiGraph:
        for node in graph.nodes():
            if 'pagerank' in graph.nodes[node]:
                del graph.nodes[node]['pagerank']
        return graph 
    
    def delete_rank(self, graph: nx.DiGraph) -> nx.DiGraph:
        for node in graph.nodes():
            if 'pagerank' in graph.nodes[node]:
                del graph.nodes[node]['rank']
        return graph 
    
    def expand_target_node(self, targetnode: str, graph: nx.DiGraph, depth: int, retries: int) -> nx.DiGraph:
        """Expand the target node by generating new topics."""
        has_child_node = any(edge[0] == targetnode for edge in graph.edges())

        generator = Generator(client=self.client)

        if has_child_node:
            # Case 1: The target node has child nodes
            topics = [
                self.get_child_topic_desc(edge[1], graph)
                for edge in graph.edges()
                if edge[0] == targetnode
            ]
            combined_topics = ", ".join(topics)
            prompt = f"I want you to only generate topics about the {targetnode} but I want the topic to be an extra topic that does not exist in these topics: {combined_topics}"
        else:
            # Case 2: The target node does not have child nodes
            prompt = f"I want you to generate extra topics about the {targetnode}"

        expanded_graph = generator.generate_roadmap(prompt=prompt, depth=depth, retries=retries)

        # Redundant_fixer = RedundantFunc(client=self.client)
        websearch = ResourceFinder(SERPER_API_KEY=self.SERPER_API_KEY)
        pagerank = ranker()
        graphfix = GraphFixer()
        titlesort = sortpgscore()

        graph = self.delete_pagerank(graph)
        graph = self.delete_rank(graph)

        # expanded_graph = Redundant_fixer.remove_redundant_nodes(graph=expanded_graph, retries=retries)
        expanded_graph = websearch.serp_recommendation_graph(graph=expanded_graph, SERPER_API_KEY=self.SERPER_API_KEY)

        expanded_graph = self.connect_expanded_graph(graph, expanded_graph, targetnode)
        expanded_graph = graphfix.fix_graph(expanded_graph)
        expanded_graph = pagerank.get_page_rank(expanded_graph)
        expanded_graph = titlesort.graphsortattribute(expanded_graph)
        
        return expanded_graph
    


