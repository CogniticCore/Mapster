import os
from dotenv import load_dotenv

import json

from fastapi import FastAPI, Depends, HTTPException, Security, Query, File, UploadFile
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from fastapi.middleware.cors import CORSMiddleware

import networkx as nx
from src import RoadmapGen as rmg

import instructor
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Define the list of allowed origins
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "https://mapster-cogniticcore.onrender.com",
    "https://mapster-front-end.vercel.app",
    "https://www.cogniticcore.xyz",
]

# Add CORSMiddleware to the app with restricted methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key configurations
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "access_token"
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_KEY_NAME = "access_token"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
serper_api_key_header = APIKeyHeader(name=SERPER_API_KEY_NAME, auto_error=False)
serper_api_key_query = APIKeyQuery(name=SERPER_API_KEY_NAME, auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header), api_key_query: str = Security(api_key_query)):
    """
    Validate the API key provided in the request.
    
    Returns:
    str: The valid API key.
    
    Raises:
    HTTPException: If the API key is invalid.
    """
    if api_key_header == API_KEY or api_key_query == API_KEY:
        return API_KEY
    else:
        raise HTTPException(status_code=403, detail="Could not validate OpenAi credentials")
    
async def get_serper_api_key(serper_api_key_header: str = Security(serper_api_key_header), serper_api_key_query: str = Security(serper_api_key_query)):
    """
    Validate the Serper API key provided in the request.
    
    Returns:
    str: The valid Serper API key.
    
    Raises:
    HTTPException: If the Serper API key is invalid.
    """
    if serper_api_key_header == SERPER_API_KEY or serper_api_key_query == SERPER_API_KEY:
        return SERPER_API_KEY
    else:
        raise HTTPException(status_code=403, detail="Could not validate Serper credentials")
    
@app.get("/graph/Full")
async def get_graph_full(
    openai_api_key: str = Query(get_api_key),
    serper_api_key: str = Query(get_serper_api_key),
    prompt: str = Query(..., description="The prompt for the LLM"),
    depth: int = Query(3, description="The depth of the roadmap"),
    retries: int = Query(2, description="The number of retries for the LLM call")
):
    print('A request has been made')
    """
    Generate a full learning roadmap with all cleaning and ranking steps.
    
    Parameters:
    openai_api_key (str): OpenAI API key.
    serper_api_key (str): Serper API key.
    prompt (str): The prompt for the LLM.
    depth (int): The depth of the roadmap.
    retries (int): The number of retries for the LLM call.
    
    Returns:
    dict: The cleaned and ranked learning roadmap.
    """
    client = instructor.from_openai(OpenAI(api_key=openai_api_key))
    generator = rmg.Generator(client=client)
    websearch = rmg.ResourceFinder(SERPER_API_KEY=serper_api_key)
    pagerank = rmg.ranker()
    graphfix = rmg.GraphFixer()
    titlesort = rmg.sortpgscore()

    roadmap = generator.generate_roadmap(prompt=prompt, depth=depth, retries=retries)
    cleaned_roadmap = websearch.serp_recommendation_graph(graph=roadmap, SERPER_API_KEY=serper_api_key)
    cleaned_roadmap = pagerank.get_page_rank(graph=cleaned_roadmap)
    cleaned_roadmap = graphfix.fix_graph(cleaned_roadmap)
    cleaned_roadmap = titlesort.graphsortattribute(cleaned_roadmap)

    cleaned_roadmap = nx.node_link_data(cleaned_roadmap)
    cleaned_roadmap['prompt'] = prompt
    return cleaned_roadmap

@app.post("/graph/ExpandNode")
async def expand_node(
    openai_api_key: str = Query(get_api_key),
    serper_api_key: str = Query(get_serper_api_key),
    upload_file: UploadFile = File(...),
    depth: int = Query(3, description="The depth of the roadmap"),
    retries: int = Query(2, description="The number of retries for the LLM call"),
    target_node: str = Query(..., description="Target node ID")
):
    """
    Expand a specific node in the roadmap.
    
    Parameters:
    openai_api_key (str): OpenAI API key.
    serper_api_key (str): Serper API key.
    upload_file (UploadFile): The uploaded roadmap file.
    depth (int): The depth of the roadmap.
    retries (int): The number of retries for the LLM call.
    target_node (str): The ID of the target node to expand.
    
    Returns:
    dict: The expanded learning roadmap.
    """
    json_data = json.load(upload_file.file)
    client = instructor.from_openai(OpenAI(api_key=openai_api_key))
    nodeexpander = rmg.NodeExpand(client=client, SERPER_API_KEY=serper_api_key)
    expanded_roadmap = nodeexpander.expand_target_node(target_node, graph=nx.node_link_graph(json_data), depth=depth, retries=retries)
    return nx.node_link_data(expanded_roadmap)

@app.get("/graph")
async def get_graph(
    openai_api_key: str = Query(get_api_key),
    prompt: str = Query(..., description="The prompt for the LLM"),
    depth: int = Query(3, description="The depth of the roadmap"),
    retries: int = Query(2, description="The number of retries for the LLM call")
):
    """
    Generate a learning roadmap.
    
    Parameters:
    openai_api_key (str): OpenAI API key.
    prompt (str): The prompt for the LLM.
    depth (int): The depth of the roadmap.
    retries (int): The number of retries for the LLM call.
    
    Returns:
    dict: The generated learning roadmap.
    """
    client = instructor.from_openai(OpenAI(api_key=openai_api_key))
    generator = rmg.Generator(client=client)
    roadmap = generator.generate_roadmap(prompt=prompt, depth=depth, retries=retries)

    cleaned_roadmap = nx.node_link_data(roadmap)
    cleaned_roadmap['prompt'] = prompt
    return cleaned_roadmap

@app.post("/mergegraph")
async def merge_graph(
    openai_api_key: str = Query(get_api_key),
    upload_file: UploadFile = File(...),
    retries: int = Query(2, description="The number of retries for the LLM call")
):
    """
    Merge nodes in the roadmap to remove redundancy.
    
    Parameters:
    openai_api_key (str): OpenAI API key.
    upload_file (UploadFile): The uploaded roadmap file.
    retries (int): The number of retries for the LLM call.
    
    Returns:
    dict: The roadmap with redundant nodes removed.
    """
    json_data = json.load(upload_file.file)
    client = instructor.from_openai(OpenAI(api_key=openai_api_key))
    redundant_fixer = rmg.RedundantFunc(client=client)
    roadmap = redundant_fixer.remove_redundant_nodes(graph=nx.node_link_graph(json_data), retries=retries)
    return nx.node_link_data(roadmap)

@app.post("/graph/resources")
async def get_resources(
    serper_api_key: str = Query(get_serper_api_key),
    upload_file: UploadFile = File(...),
    retries: int = Query(2, description="The number of retries for the LLM call")
):
    """
    Get recommended resources for the roadmap.
    
    Parameters:
    serper_api_key (str): Serper API key.
    upload_file (UploadFile): The uploaded roadmap file.
    retries (int): The number of retries for the LLM call.
    
    Returns:
    dict: The roadmap with recommended resources.
    """
    json_data = json.load(upload_file.file)
    websearch = rmg.ResourceFinder(SERPER_API_KEY=serper_api_key)
    roadmap = websearch.serp_recommendation_graph(graph=nx.node_link_graph(json_data), SERPER_API_KEY=serper_api_key)
    return nx.node_link_data(roadmap)

@app.post("/graph/pageranker")
async def page_ranker(upload_file: UploadFile = File(...)):
    """
    Apply PageRank algorithm to the roadmap.
    
    Parameters:
    upload_file (UploadFile): The uploaded roadmap file.
    
    Returns:
    dict: The roadmap with PageRank scores.
    """
    json_data = json.load(upload_file.file)
    pagerank = rmg.ranker()
    roadmap = pagerank.get_page_rank(graph=nx.node_link_graph(json_data))
    return nx.node_link_data(roadmap)

@app.post("/graph/tree")
async def graph_to_tree(upload_file: UploadFile = File(...)):
    """
    Convert a graph to a tree structure.
    
    Parameters:
    upload_file (UploadFile): The uploaded roadmap file.
    
    Returns:
    dict: The roadmap as a tree structure.
    """
    json_data = json.load(upload_file.file)
    graphfix = rmg.GraphFixer()
    roadmap = graphfix.fix_graph(graph=nx.node_link_graph(json_data))
    return nx.node_link_data(roadmap)

@app.post("/graphranking")
async def get_graph_ranking(upload_file: UploadFile = File(...)):
    """
    Sort the roadmap by PageRank scores.
    
    Parameters:
    upload_file (UploadFile): The uploaded roadmap file.
    
    Returns:
    dict: The sorted roadmap.
    """
    json_data = json.load(upload_file.file)
    titlesort = rmg.sortpgscore()
    roadmap = titlesort.graphsortattribute(graph=nx.node_link_graph(json_data))
    return nx.node_link_data(roadmap)