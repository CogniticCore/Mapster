import os
from dotenv import load_dotenv

import json

from fastapi import FastAPI, Depends, HTTPException, Security, Query, File, UploadFile, Header, Body
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import BaseModel, constr
from typing import Optional, Dict

import networkx as nx
from src import RoadmapGen as rmg

import instructor
from openai import OpenAI

from datetime import datetime, timezone

from time import time

import hashlib

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
    "https://mapster-front-end.vercel.app/demo",
    "https://www.cogniticcore.xyz",
]

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

# Add CORSMiddleware to the app with restricted methods

@app.get("/")
def read_root():
    return {"message": "Welcome to the Mapster"}

class PayloadModel(BaseModel):
    openai_api_key: str
    serper_api_key: str
    prompt: str
    depth: int
    retries: int

class CallRequestModel(BaseModel):
    method: str
    payload: PayloadModel

# Define a model for the header validation
class CallHeaders(BaseModel):
    x_marketplace_token: str
    x_request_id: str
    x_user_id: str
    x_user_role: Optional[str] = None

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_role

    @classmethod
    def validate_role(cls, value: str) -> str:
        valid_roles = ["admin", "user", "publisher"]
        if value and value not in valid_roles:
            raise ValueError(f"Invalid user role: {value}. Must be one of {valid_roles}.")
        return value
    
class ErrorCode(BaseModel):
    status: str
    reason: str

class ResponseData(BaseModel):
    dataType: str
    data: dict
    
class ResponseModel(BaseModel):
    apiVersion: str
    service: str
    datetime: str
    processDuration: float
    taskId: str
    isResponseImmediate: bool
    extraType: str
    response: ResponseData
    errorCode: ErrorCode

class StatusCodes:
    # Task stage
    SUCCESS = "AC_000"         # Task completed successfully
    PENDING = "AC_001"         # Task is pending
    INPROGRESS = "AC_002"      # Task is currently in progress
    
    # Client Errors
    INVALID_REQUEST = "AC_400" # Empty, null, or invalid field in payload
    EXCEEDING_PERMITTED_RESOURCES = "AC_401" # Exceeded allowed time/resources
    RESOURCE_DOES_NOT_EXIST = "AC_402" # Resource not found (e.g., melody)
    UNSUPPORTED = "AC_403"     # Unsupported resource type (e.g., non-mp3 melody)
    
    # Server Errors
    TIMEOUT = "AC_500"         # Task timeout
    ERROR = "AC_501"           # Unknown error
    RABBIT_ERROR = "AC_502"    # RabbitMQ connection error
    REDIS_ERROR = "AC_503"     # Redis connection error (adjusted the code)
    S3_ERROR = "AC_504"        # S3 connection error

def generate_task_id(data: Dict) -> str:
    # Convert the dictionary to a sorted JSON string to ensure consistent hashing
    json_str = json.dumps(data, sort_keys=True)
    
    # Create a SHA-256 hash of the JSON string
    hash_object = hashlib.sha256(json_str.encode())
    
    # Return the hexadecimal representation of the hash
    return hash_object.hexdigest()

@app.post("/result")
async def get_result(
    x_marketplace_token: str = Header(...),
    x_request_id: str = Header(...),
    x_user_id: str = Header(...),
    x_user_role: Optional[str] = Header(None),
    body: CallRequestModel = Body(...)
):  
    start_time = time.time()
    print('A request has been made')

    x_marketplace_token = x_marketplace_token.strip()
    x_request_id = x_request_id.strip()
    x_user_id = x_user_id.strip()
    if x_user_role:
        x_user_role = x_user_role.strip()

    if not x_marketplace_token:
        raise HTTPException(status_code=400, detail="Missing x-marketplace-token header")
    if not x_request_id:
        raise HTTPException(status_code=400, detail="Missing x-request-id header")
    if not x_user_id:
        raise HTTPException(status_code=400, detail="Missing x-user-id header")
    
    method = body.method
    payload = body.payload

    if method not in ["graphfull"]:
        raise HTTPException(status_code=400, detail="Invalid method. Supported method is 'graphfull'")
    
    openai_api_key = payload.openai_api_key
    serper_api_key = payload.serper_api_key
    prompt = payload.prompt
    depth = payload.depth
    retries = payload.retries
    
    unique_data = {
        "x_marketplace_token": x_marketplace_token,
        "x_request_id": x_request_id,
        "x_user_id": x_user_id,
        "x_user_role": x_user_role,
        "method": method,
        "openai_api_key": payload.openai_api_key,
        "serper_api_key": payload.serper_api_key,
        "prompt": payload.prompt,
        "depth": payload.depth,
        "retries": payload.retries
    }
    task_id = generate_task_id(unique_data)


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

    end_time = time.time()
    process_duration = end_time - start_time

    #change format to store in db
    response = {
        "apiVersion": "v1",
        "service": "graphfull",
        "datetime": datetime.now(timezone.utc).isoformat(),
        "processDuration": process_duration,
        "taskId": task_id,  # Replace with actual task ID if available
        "isResponseImmediate": False,  # Replace with actual value if needed
        "response" :{
            "dataType": "DICT",
            "data": cleaned_roadmap
        },
        "errorCode": {
            "status": StatusCodes.SUCCESS,
            "reason": "success"
        }
    }

    return response
    



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)