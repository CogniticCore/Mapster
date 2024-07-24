import http.client
from typing import List, Dict
import json
from tqdm import tqdm
import networkx as nx

class ResourceFinder:
    def __init__(self, SERPER_API_KEY):
        self.SERPER_API_KEY = SERPER_API_KEY
        
    def call_serp(self, query: List[str], SERPER_API_KEY: str):
        # Establish connection to the SERPER API
        conn = http.client.HTTPSConnection("google.serper.dev")

        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

        query_json = [{"q": i} for i in query]
        payload = json.dumps(query_json)

        conn.request("POST", "/search", payload, headers)

        res = conn.getresponse()
        data = res.read()

        return json.loads(data.decode("utf-8"))

    def serp_recommendation(self, topic: str, SERPER_API_KEY: str) -> Dict[str, List[Dict[str, str]]]:
        query = [
            f'{topic} Books filetype:pdf',
            f'{topic} Video',
            f'{topic} Course OR Workshop'
        ]

        serp_result = self.call_serp(query=query, SERPER_API_KEY=SERPER_API_KEY)

        # Extract top 3 results for books, videos, and courses/workshops
        recommend_books = serp_result[0]['organic'][:3]
        recommend_videos = serp_result[1]['organic'][:3]
        recommend_courses = serp_result[2]['organic'][:3]

        return {
            "recommend_books": recommend_books,
            "recommend_videos": recommend_videos,
            "recommend_courses": recommend_courses
        }

    def serp_recommendation_graph(self, graph: nx.DiGraph, SERPER_API_KEY: str) -> nx.DiGraph:
        for node in tqdm(graph.nodes):
            new_attrs = {node : self.serp_recommendation(node, SERPER_API_KEY)}
            old_attrs = graph.nodes[node]
            nx.set_node_attributes(graph, {**old_attrs, **new_attrs})
        return graph