import networkx as nx

from ..core.RoadmapGenerator import Generator
from .pagerank import ranker
from .nodefixer import GraphFixer
from .jsonranker import sortpgscore
from .websearch import ResourceFinder

class NodeExpand:
    def __init__(self, client, SERPER_API_KEY: str):
        self.client = client
        self.SERPER_API_KEY = SERPER_API_KEY

    def get_child_topic_desc(self, targetnode: str, graph: nx.DiGraph) -> str:
        """
        Get the description of a child topic.
        
        Parameters:
        targetnode (str): The target node ID.
        graph (nx.DiGraph): The roadmap graph.
        
        Returns:
        str: The title of the target node.
        """
        try:
            for node, data in graph.nodes(data=True):
                if node == targetnode:
                    return data.get('title', '')
        except ValueError as e:
            print(f"Error: {e}")
        return ''

    def connect_expanded_graph(self, original_graph: nx.DiGraph, expanded_graph: nx.DiGraph, targetnode: str) -> nx.DiGraph:
        """
        Connect the expanded graph to the original graph.
        
        Parameters:
        original_graph (nx.DiGraph): The original roadmap graph.
        expanded_graph (nx.DiGraph): The expanded roadmap graph.
        targetnode (str): The target node ID.
        
        Returns:
        nx.DiGraph: The connected roadmap graph.
        """
        for node, data in expanded_graph.nodes(data=True):
            if node != targetnode:
                original_graph.add_node(node, **data)
                original_graph.add_edge(targetnode, node)

        for edge in expanded_graph.edges(data=True):
            original_graph.add_edge(edge[0], edge[1], **edge[2])

        return original_graph
    
    def delete_pagerank(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Delete PageRank attribute from the graph nodes.
        
        Parameters:
        graph (nx.DiGraph): The roadmap graph.
        
        Returns:
        nx.DiGraph: The roadmap graph without PageRank attribute.
        """
        for node in graph.nodes():
            if 'pagerank' in graph.nodes[node]:
                del graph.nodes[node]['pagerank']
        return graph 
    
    def delete_rank(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Delete rank attribute from the graph nodes.
        
        Parameters:
        graph (nx.DiGraph): The roadmap graph.
        
        Returns:
        nx.DiGraph: The roadmap graph without rank attribute.
        """
        for node in graph.nodes():
            if 'rank' in graph.nodes[node]:
                del graph.nodes[node]['rank']
        return graph 
    
    def expand_target_node(self, targetnode: str, graph: nx.DiGraph, depth: int, retries: int) -> nx.DiGraph:
        """
        Expand the target node by generating new topics.
        
        Parameters:
        targetnode (str): The target node ID.
        graph (nx.DiGraph): The roadmap graph.
        depth (int): The depth of the roadmap.
        retries (int): The number of retries for the LLM call.
        
        Returns:
        nx.DiGraph: The expanded roadmap graph.
        """
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

        websearch = ResourceFinder(SERPER_API_KEY=self.SERPER_API_KEY)
        pagerank = ranker()
        graphfix = GraphFixer()
        titlesort = sortpgscore()

        graph = self.delete_pagerank(graph)
        graph = self.delete_rank(graph)

        expanded_graph = websearch.serp_recommendation_graph(graph=expanded_graph, SERPER_API_KEY=self.SERPER_API_KEY)
        expanded_graph = self.connect_expanded_graph(graph, expanded_graph, targetnode)
        expanded_graph = graphfix.fix_graph(expanded_graph)
        expanded_graph = pagerank.get_page_rank(expanded_graph)
        expanded_graph = titlesort.graphsortattribute(expanded_graph)
        
        return expanded_graph
