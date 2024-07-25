from ..core.RoadmapGenerator import Generator
from .RedunRemover import RedundantFunc
from .websearch import ResourceFinder
from .pagerank import ranker
from typing import List, Dict
import networkx as nx

class NodeExpand:
    def __init__(self, client, SERPER_API_KEY):
        self.client=client
        self.SERPER_API_KEY = SERPER_API_KEY

    def get_child_topic_desc(self, targetnode: str, graph: Dict) -> str:
        try:
            for node in graph['nodes']:
                if node['id'] == targetnode:
                    return node['id']
        except ValueError as e:
            print(f"Error: {e}")
        return ''

    def connect_expanded_graph(self, original_graph: nx.Graph, expanded_graph: nx.Graph, targetnode: str) -> nx.Graph:
        for node in expanded_graph.nodes:
            if node != targetnode:
                original_graph.add_node(node, **expanded_graph.nodes[node])
                original_graph.add_edge(targetnode, node)

        for edge in expanded_graph.edges:
            original_graph.add_edge(edge[0], edge[1], **expanded_graph.edges[edge])

        return original_graph
    
    def expand_target_node(self, targetnode: str, graph: Dict, depth: int, retries: int) -> nx.Graph:
        """Expand the target node by generating new topics."""
        nx_graph = nx.node_link_graph(graph)
        has_child_node = any(link['source'] == targetnode for link in graph['links'])

        generator = Generator(client=self.client)

        if has_child_node:
            # Case 1: The target node has child nodes
            topics = [
                self.get_child_topic_desc(link['target'], graph)
                for link in graph['links']
                if link['source'] == targetnode
            ]
            combined_topics = ", ".join(topics)
            prompt = f"I want you to only generate topics about the {targetnode} but I want the topic to be an extra topic that does not exist in these topics: {combined_topics}"
        else:
            # Case 2: The target node does not have child nodes
            prompt = f"I want you to generate extra topics about the {targetnode}"

        expanded_graph = generator.generate_roadmap(prompt=prompt, depth=depth, retries=retries)
        # expanded_graph = nx.node_link_graph(expanded_node)

        Redundant_fixer = RedundantFunc(client=self.client)
        websearch = ResourceFinder(SERPER_API_KEY = self.SERPER_API_KEY)
        pagerank = ranker()

        expanded_graph = Redundant_fixer.remove_redundant_nodes(graph = expanded_graph, retries = retries)
        expanded_graph = websearch.serp_recommendation_graph(graph = expanded_graph, SERPER_API_KEY =  self.SERPER_API_KEY)
        expanded_graph = pagerank.get_page_rank(graph = expanded_graph)

        return self.connect_expanded_graph(nx_graph, expanded_graph, targetnode)
    


