from tqdm import tqdm
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
from typing import List
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
    def call_llm(self,prompt):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=TopicInfo,
            messages=[
                    {"role": "system", "content": "You are learning roadmap planner for a main topic, you will be given a current topic and you have to provide a list of prerequisite topic and description"},
                    {"role": "user", "content": prompt}
                ]
        )
        return completion.topic, completion.description, completion.prerequisite_topics, completion.description_prerequisite_topics

    def clean_text(self,text: str):
        return text.replace(':', '-')

    def generate_roadmap(self,prompt: str, depth: int, retry: int):
        graph = nx.DiGraph()
        root_topic, root_description, root_prerequisites, root_description_prerequisites = self.call_llm(prompt)
        i = retry
        while len(root_prerequisites) != len(root_description_prerequisites) and i > 0:
            root_topic, root_description, root_prerequisites, root_description_prerequisites = self.call_llm(prompt)
            i -= 1

        root_topic = self.clean_text(root_topic)
        root_description = self.clean_text(root_description)
        root_prerequisites = [self.clean_text(x) for x in root_prerequisites]
        root_description_prerequisites = [self.clean_text(x) for x in root_description_prerequisites]

        graph.add_node(root_topic, description = root_description)

        for topic, description in tqdm(zip(root_prerequisites, root_description_prerequisites)):
            graph.add_node(topic, description = description)
            graph.add_edge(root_topic, topic)

        for i in range(depth-1):
            leaf_node = [x for x in graph.nodes() if graph.out_degree(x)==0]

            for topic in tqdm(leaf_node):
                _, _, child_prerequisites, child_description_prerequisites = self.call_llm(Prompt.LlmPrompt.getprompt().format(main_topic = root_topic, current_topic = topic, current_description = graph.nodes[topic]['description']))

                i = retry
                while len(child_prerequisites) != len(child_description_prerequisites) and i > 0:
                    _, _, child_prerequisites, child_description_prerequisites = self.call_llm(Prompt.LlmPrompt.getprompt().format(root_topic, current_topic = topic, current_description = graph.nodes[topic]['description']))
                    i -= 1
                    print('wow')

                child_prerequisites = [self.clean_text(x) for x in child_prerequisites]
                child_description_prerequisites = [self.clean_text(x) for x in child_description_prerequisites]

                for child_topic, child_description in zip(child_prerequisites, child_description_prerequisites):
                    graph.add_node(child_topic, description = child_description)
                    graph.add_edge(topic, child_topic)

        return graph