import hashlib
import networkx as nx
from tqdm import tqdm
from typing import Dict
class GraphFixer:
    def _generate_hash_id(self, node_id :str, src: str, node_data: Dict) -> str:
        """Generate a unique hash ID based on the node ID, source, and its data."""
        content = f"{node_id}-{src}-{node_data}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def fix_graph(self, graph: nx.DiGraph) -> nx.DiGraph:
        node_id_to_hash = {}
        new_graph = nx.DiGraph()

        for node in tqdm(graph.nodes(), desc="Processing nodes"):
            in_edges = list(graph.in_edges(node))
            node_data = graph.nodes[node]

            if len(in_edges) > 1:
                # Duplicate child node for each parent (multiple incoming edges)
                for src, _ in in_edges:
                    new_hash_id = self._generate_hash_id(node, src, node_data)
                    node_id_to_hash[(node, src)] = new_hash_id
                    new_node_data = node_data.copy()
                    new_node_data['title'] = node
                    new_graph.add_node(new_hash_id, **new_node_data)
            elif in_edges:
                src = in_edges[0][0]
                new_hash_id = self._generate_hash_id(node, src, node_data)
                node_id_to_hash[(node, src)] = new_hash_id
                new_node_data = node_data.copy()
                new_node_data['title'] = node
                new_graph.add_node(new_hash_id, **new_node_data)
            else:
                # Root nodes / no incoming edge nodes
                new_hash_id = self._generate_hash_id(node, None, node_data)
                node_id_to_hash[(node, None)] = new_hash_id
                new_node_data = node_data.copy()
                new_node_data['title'] = node
                new_graph.add_node(new_hash_id, **new_node_data)

        for src, tgt in tqdm(graph.edges(), desc="Adding edges"):
            for (src_node, tgt_node) in graph.edges():
                new_src_hash = node_id_to_hash.get((src_node, src), node_id_to_hash.get((src_node, None)))
                new_tgt_hash = node_id_to_hash.get((tgt_node, src_node), node_id_to_hash.get((tgt_node, None)))

                if new_src_hash and new_tgt_hash:
                    new_graph.add_edge(new_src_hash, new_tgt_hash, **graph.get_edge_data(src_node, tgt_node))
                    # print(f"Debug: Creating edge from {new_src_hash} to {new_tgt_hash} (original {src_node} -> {tgt_node})")

        return new_graph
