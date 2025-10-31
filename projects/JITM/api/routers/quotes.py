"""JITM ${router^} Router - To be implemented"""
from fastapi import APIRouter
router = APIRouter()
@router.get("/")
async def list_items():
    return {"message": "Coming soon"}
