from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
from tqdm import tqdm
import networkx as nx

# Define a RedundantGroup class to structure the LLM response for redundant nodes
class RedundantGroup(BaseModel):
    group: List[List[str]] = Field(description="List of List of similar/redundant topic groups")

# Define a MergedTopic class to structure the LLM response for merging nodes
class MergedTopic(BaseModel):
    topic: str = Field(description="The merged topic of redundant topics")
    description: str = Field(description="The description of this topic")

class RedundantFunc:
    def __init__(self, client):
        self.client = client

    def clean_text(self,text: str):
        return text.replace(':', '-')
    
    # Function to merge lists of redundant nodes
    def merge_redundant_lists(self, lists: List[List[str]]) -> List[List[str]]:
        merged_lists = []

        while lists:
            first, *rest = lists
            first = set(first)
            combined = first

            rest_copy = rest[:]
            for lst in rest_copy:
                if first.intersection(lst):
                    combined.update(lst)
                    rest.remove(lst)

            merged_lists.append(list(combined))
            lists = rest

        return merged_lists
    
    # Function to call the LLM for merging redundant topics
    def call_llm_redundant_grouper(self, prompt: str, retries: int = 3) -> Tuple[str, str]:
        for _ in range(retries):
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=RedundantGroup,
                temperature=0,
                max_retries=0,
                messages=[
                    {"role": "system", "content": "You are a learning roadmap planner for a main topic. You will be given a list of prerequisite topics. Your task is to identify and group redundant or similar topics."},
                    {"role": "user", "content": prompt}
                ]
            )
            if completion.group:
                return completion.group
        raise ValueError("Failed to group redundant topics after retries")
    
    # Function to call the LLM for merging redundant topics
    def call_llm_redundant_merger(self, prompt: str, retries: int = 3) -> Tuple[str, str]:
        for _ in range(retries):
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=MergedTopic,
                messages=[
                    {"role": "system", "content": "You are a redundant topic merger for a main topic. You will be given a list of redundant topics and you have to provide a merged topic and description."},
                    {"role": "user", "content": prompt}
                ]
            )
            if completion.topic and completion.description:
                return completion.topic, completion.description
        raise ValueError("Failed to merge redundant topics after retries")
    
    # Function to remove redundant nodes from the graph
    def remove_redundant_nodes(self, graph: nx.DiGraph, retries: int = 3) -> nx.DiGraph:
        root_topic = [n for n, d in graph.in_degree() if d == 0][0]

        node_text = ''.join(f"{node}\t{graph.nodes[node]['description']}\n" for node in graph.nodes)

        redundant_list = self.call_llm_redundant_grouper(node_text)
        redundant_list = self.merge_redundant_lists(redundant_list)

        for redundant in tqdm(redundant_list, desc="Merging redundant nodes"):
            node_text = ''.join(f"{topic}\t{graph.nodes[topic]['description']}\n" for topic in redundant if topic in graph.nodes)
            # Ensure merged_topic is a string or another hashable type
            merged_topic, merged_description = self.call_llm_redundant_merger(
                prompt=node_text,
                retries=retries
            )

            merged_topic = self.clean_text(merged_topic)
            merged_description = self.clean_text(merged_description)

            graph.add_node(merged_topic, description=merged_description)

            for topic in redundant:
                if topic in graph.nodes:
                    for parent in graph.predecessors(topic):
                        graph.add_edge(parent, merged_topic)
                    for _, child in graph.edges(topic):
                        graph.add_edge(merged_topic, child)
                    graph.remove_node(topic)
            graph.remove_edges_from(nx.selfloop_edges(graph))
            graph.remove_nodes_from(list(nx.isolates(graph)))
        return graph
    #meow