import uvicorn
from fastapi import FastAPI
from prisma import Prisma
from src.routes import cases
from src.scripts.cases import get_case_prices


app = FastAPI()

app.include_router(cases.router, prefix="")


@app.post("/load_case_prices/")
async def load_case_prices():
    await get_case_prices()
 
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
