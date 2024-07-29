from typing import List, Tuple
import networkx as nx

class sortpgscore:
    def sortscore(self, graph: nx.DiGraph) -> List[Tuple[float, str]]:
        pairs: List[Tuple[float, str]] = []
        for node in graph.nodes():
            node_data = graph.nodes[node]
            pagerank = node_data.get('pagerank', 0.0)  # Default 0.0
            title = node_data.get('title', '')  # Default ''
            pairs.append((pagerank, title))

        sorted_pairs = sorted(pairs, key=lambda x: x[0], reverse=False)
        return sorted_pairs

        
    def graphsortattribute(self, graph: nx.DiGraph) -> nx.DiGraph:
        pairs = self.sortscore(graph)
        rank = 0
        last_pagerank = None
        
        for pair_pagerank, pair_title in pairs:
            # Only increment rank if the pagerank changes
            if pair_pagerank != last_pagerank:
                last_pagerank = pair_pagerank
                rank += 1
            
            # Set the rank for all nodes with the same title
            for node in graph.nodes():
                node_data = graph.nodes[node]
                title = node_data.get('title', '')
                if title == pair_title:
                    graph.nodes[node]['rank'] = rank

        return graph
