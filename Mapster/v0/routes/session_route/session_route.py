from fastapi import APIRouter, HTTPException
from models import ResponseModel, http_exception_handler, create_response

session_route = APIRouter(
    prefix='/sessions'
)

@session_route.get('/', response_model=ResponseModel)
async def get_available_sessions():
    try:
        create_response(
            data = {'exa':'123'}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "Message": "Internal Server Error",
                "Errors": {"details": str(e)}
            }
        )
