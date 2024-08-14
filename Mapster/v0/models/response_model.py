from fastapi import HTTPException, Request
from pydantic import BaseModel
from typing import Optional

class ResponseModel(BaseModel):
    Status: str
    Message: str
    Data: Optional[dict] = None
    Error: Optional[dict] = None

def http_exception_handler(request: Request, exc: HTTPException):
    return ResponseModel(
        StopAsyncIterationtatus="error",
        Message=exc.detail.get("Message", "An error occurred"),
        Errors=exc.detail.get("Errors")
    )

def create_response(
        Status: str = "success", # or "error"
        Message: str = "Successful Request", # or "Document Not Found"
        Data: Optional[dict] = None
    ):
    return ResponseModel(
        Status=Status,
        Message=Message,
        Data=Data
    )