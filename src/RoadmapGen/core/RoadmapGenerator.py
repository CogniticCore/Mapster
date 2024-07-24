from tqdm import tqdm
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
from typing import List, Tuple
from pydantic import BaseModel, Field
from . import Prompt

class TopicInfo(BaseModel):
    topic: str = Field(
        description="The topic of the question"
    )
    description: str = Field(
        description="The description of this topic"
    )
    prerequisite_topics: List[str] = Field(
        description="A list of prerequisite topics"
    )
    description_prerequisite_topics: List[str] = Field(
        description="A list of description of prerequisite topics"
    )

class Generator:
    def __init__(self, client):
        self.client = client
    # Function to call the LLM with the given prompt
    def call_llm(self, prompt: str, model="gpt-4o-mini", retries=3) -> Tuple[str, str, List[str], List[str]]:
        for _ in range(retries):
            completion = self.client.chat.completions.create(
                model=model,
                response_model=TopicInfo,
                messages=[
                    {"role": "system", "content": "You are a learning roadmap planner for a main topic. You will be given a current topic and you have to provide a list of prerequisite topics and descriptions."},
                    {"role": "user", "content": prompt}
                ]
            )
            if len(completion.prerequisite_topics) == len(completion.description_prerequisite_topics):
                return completion.topic, completion.description, completion.prerequisite_topics, completion.description_prerequisite_topics
        raise ValueError("Mismatched prerequisite and description lengths after retries")
    
    def clean_text(self,text: str):
        return text.replace(':', '-')

    # Function to generate the knowledge graph roadmap
    def generate_roadmap(self, prompt: str, depth: int, retries: int) -> nx.DiGraph:
        graph = nx.DiGraph()
        root_topic, root_description, root_prerequisites, root_description_prerequisites = self.call_llm(prompt, retries=retries)

        root_topic = self.clean_text(root_topic)
        root_description = self.clean_text(root_description)
        root_prerequisites = [self.clean_text(x) for x in root_prerequisites]
        root_description_prerequisites = [self.clean_text(x) for x in root_description_prerequisites]

        graph.add_node(root_topic, description=root_description)

        for topic, description in zip(root_prerequisites, root_description_prerequisites):
            graph.add_node(topic, description=description)
            graph.add_edge(root_topic, topic)
            
        for current_depth in range(depth - 1):
            leaf_nodes = [node for node in graph.nodes if graph.out_degree(node) == 0]

            for topic in tqdm(leaf_nodes, desc="Expanding nodes at current depth {depth}".format(depth=current_depth + 2)):
                current_description = graph.nodes[topic]['description']
                child_topic, child_description, child_prerequisites, child_description_prerequisites = self.call_llm(
                    Prompt.LlmPrompt.getprompt().format(main_topic=root_topic, current_topic=topic, current_description=current_description),
                    retries=retries
                )

                child_prerequisites = [self.clean_text(x) for x in child_prerequisites]
                child_description_prerequisites = [self.clean_text(x) for x in child_description_prerequisites]

                for child_topic, child_description in zip(child_prerequisites, child_description_prerequisites):
                    graph.add_node(child_topic, description=child_description)
                    graph.add_edge(topic, child_topic)

        return graph