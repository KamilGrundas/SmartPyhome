from fastapi import APIRouter
from src.schemas import CasePriceModel
from src.repository import cases

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/")
async def add_case_record(body: CasePriceModel):
    return await cases.add_case_record(body)


@router.get("/")
async def get_case_records():
    return await cases.get_case_records()
