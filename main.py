from src import RoadmapGen as rmg
import instructor
from openai import OpenAI
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Security, Query
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image

load_dotenv()

# for node in list(roadmap_graph.nodes):
#     print("{:80s} : {:s}".format(node, roadmap_graph.nodes[node]['description']))

app = FastAPI()

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "access_token"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header), api_key_query: str = Security(api_key_query)):
    if api_key_header == API_KEY or api_key_query == API_KEY:
        return API_KEY
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
    
@app.get("/Getgraph")
async def secure_endpoint(
    openai_api_key: str = Query(get_api_key),
    prompt: str = Query(..., description="The prompt for the LLM"),
    depth: int = Query(3, description="The depth of the roadmap"),
    retry: int = Query(2, description="The number of retries for the LLM call")
):
    client = instructor.from_openai(OpenAI(
    api_key=openai_api_key
    ))
    generator = rmg.Generator(client=client)
    roadmap = generator.generate_roadmap(prompt, depth, retry)
    # roadmap_data = nx.node_link_data(roadmap)

    return_str = ''
    for node in list(roadmap.nodes):
      return_str+="{:80s} : {:s}".format(node, roadmap.nodes[node]['description'])
    return return_str


