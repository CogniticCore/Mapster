from fastapi import APIRouter
from .session_route import session_route

v0_route = APIRouter(
    prefix='/v0'
)

v0_route.include_router(session_route)