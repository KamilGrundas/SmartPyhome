from fastapi import APIRouter, status
from prisma.models import Case_Price
from src.repository import cases



router = APIRouter(prefix="/cases", tags=["cases"]) 


@router.post("/")
async def add_case_record(body:Case_Price):
    return await cases.add_case_record(body)