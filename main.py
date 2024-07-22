import fastapi
from src import RoadmapGen as rmg
import instructor
from openai import OpenAI

client = instructor.from_openai(OpenAI(
    api_key='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'
))
generator = rmg.Generator(client)

prompt = "How to Build an Desktop AI Assistant with custom voice from character ARONA from Blue Archive"
depth = 3
retry = 2
roadmap_graph = generator.generate_roadmap(prompt, depth, retry)

for node in list(roadmap_graph.nodes):
    print("{:80s} : {:s}".format(node, roadmap_graph.nodes[node]['description']))