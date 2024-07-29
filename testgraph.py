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
import json
from typing import List, Dict
import json

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
    

openai_api_key: str = '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'
serper_api_key: str = '2240eaed703d70fffa5bfc6930ea47569344ac88'
prompt: str = 'i want to master playing moonlight sonata'
depth: int = 3
retries: int = 2

client = instructor.from_openai(OpenAI(
api_key=openai_api_key
    ))
generator = rmg.Generator(client=client)
Redundant_fixer = rmg.RedundantFunc(client=client)
websearch = rmg.ResourceFinder(SERPER_API_KEY = serper_api_key)
pagerank = rmg.ranker()

roadmap = generator.generate_roadmap(prompt = prompt, depth = depth, retries = retries)
cleaned_roadmap = Redundant_fixer.remove_redundant_nodes(graph = roadmap, retries = retries)
cleaned_roadmap = websearch.serp_recommendation_graph(graph = cleaned_roadmap, SERPER_API_KEY =  serper_api_key)
cleaned_roadmap = pagerank.get_page_rank(graph = cleaned_roadmap)

# cleaned_roadmap = nx.node_link_data(cleaned_roadmap)

# Define the file path
file_path = 'datatest.json'

# Write JSON data to a file
with open(file_path, 'w') as json_file:
    json.dump(cleaned_roadmap, json_file, indent=4)

print(f"Data has been saved to {file_path}")