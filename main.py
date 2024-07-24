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
from fastapi import FastAPI, Depends, HTTPException, Security, Query, File, UploadFile
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image
import json
from typing import List, Dict
from tqdm import tqdm


load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_KEY_NAME = "access_token"
SERPER_api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
SERPER_api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header), api_key_query: str = Security(api_key_query)):
    if api_key_header == API_KEY or api_key_query == API_KEY:
        return API_KEY
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate OpenAi credentials",
        )
    
async def get_serper_api_key(SERPER_api_key_header: str = Security(SERPER_api_key_header), SERPER_api_key_query: str = Security(SERPER_api_key_query)):
    if SERPER_api_key_header == SERPER_API_KEY or SERPER_api_key_query == SERPER_API_KEY:
        return SERPER_API_KEY
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate Serper credentials",
        )
    
@app.get("/GetgraphFull")
async def secure_endpoint(
    openai_api_key: str = Query(get_api_key),
    serper_api_key: str = Query(get_serper_api_key),
    prompt: str = Query(..., description="The prompt for the LLM"),
    depth: int = Query(3, description="The depth of the roadmap"),
    retries: int = Query(2, description="The number of retries for the LLM call"),
    redunretries: int = Query(2, description="The number of retries for the redundancy node LLM call")
):
    client = instructor.from_openai(OpenAI(
    api_key=openai_api_key
    ))
    generator = rmg.Generator(client=client)
    Redundant_fixer = rmg.RedundantFunc(client=client)
    websearch = rmg.ResourceFinder(SERPER_API_KEY = serper_api_key)
    pagerank = rmg.ranker()

    roadmap = generator.generate_roadmap(prompt = prompt, depth = depth, retries = redunretries)
    cleaned_roadmap = Redundant_fixer.remove_redundant_nodes(graph=roadmap, retries = retries)
    cleaned_roadmap = websearch.serp_recommendation_graph(graph = cleaned_roadmap, SERPER_API_KEY =  serper_api_key)
    cleaned_roadmap = pagerank.get_page_rank(graph = cleaned_roadmap)

    cleaned_roadmap = nx.node_link_data(cleaned_roadmap)
    return cleaned_roadmap

@app.post("/ExpandNode")
async def create_upload_files(
    openai_api_key: str = Query(get_api_key),
    upload_file: UploadFile = File(...),
    prompt: str = Query(..., description="The prompt for the LLM"),
    depth: int = Query(3, description="The depth of the roadmap"),
    retry: int = Query(2, description="The number of retries for the LLM call"),
    target_node: str = Query(..., description="target node id")
):
    json_data = json.load(upload_file.file)
    #mapping nodes
    node_id_map = {node['id']: node for node in json_data['nodes']}
    def get_node_by_id(node_id):
        return node_id_map.get(node_id)
    return get_node_by_id("Audio Engineering")
