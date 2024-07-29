import hashlib
import networkx as nx
from tqdm import tqdm

class GraphFixer:
    def _generate_hash_id(self, node_id, node_data):
        """Generate a unique hash ID based on the node ID and its data."""
        content = f"{node_id}-{node_data}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def fix_graph(self, graph: nx.DiGraph) -> nx.DiGraph:
        # Dictionary to map original node IDs to their new hash_id
        node_id_to_hash = {}

        # Iterate over each node in the graph
        for node in tqdm(list(graph.nodes), desc="Generating hash_id for nodes"):
            node_data = graph.nodes[node]
            new_hash_id = self._generate_hash_id(node, node_data)
            node_id_to_hash[node] = new_hash_id
            
            # Add the hash_id as an attribute to the node, keeping the original ID
            graph.nodes[node]['hash_id'] = new_hash_id
        
        # Create a new graph with edges updated to use hash_id
        new_graph = nx.DiGraph()
        for node in graph.nodes(data=True):
            new_graph.add_node(node[0], **node[1])
        
        for src, tgt in tqdm(graph.edges(), desc="Updating edges with hash_id"):
            new_src = node_id_to_hash[src]
            new_tgt = node_id_to_hash[tgt]
            new_graph.add_edge(new_src, new_tgt, **graph.get_edge_data(src, tgt))
        
        return new_graph