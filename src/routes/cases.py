from fastapi import APIRouter, status
from src.schemas import Case_Price_Model
from src.repository import cases



router = APIRouter(prefix="/cases", tags=["cases"]) 


@router.post("/")
async def add_case_record(body:Case_Price_Model):
    return await cases.add_case_record(body)

@router.get("/")
async def get_case_records():
    return await cases.get_case_records()