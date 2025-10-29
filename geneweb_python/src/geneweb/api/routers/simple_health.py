"""
Simple health check endpoint for Fly.io
No dependencies, just returns OK
"""

from fastapi import APIRouter, Response

router = APIRouter(tags=["health"])


@router.get("/")
async def simple_health():
    """Ultra simple health check for Fly.io"""
    return {"status": "ok"}


@router.get("/ping")
async def ping():
    """Ping endpoint"""
    return Response(content="pong", media_type="text/plain")
