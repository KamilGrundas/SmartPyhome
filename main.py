import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from src.routes import cases, camera
from src.scripts.cases import get_case_prices
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.include_router(cases.router, prefix="")
app.include_router(camera.router, prefix="")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
   return templates.TemplateResponse('index.html', {"request": request})

@app.post("/load_case_prices/")
async def load_case_prices():
    await get_case_prices()


if __name__ == "__main__":
    uvicorn.run(app, host="192.168.1.128", port=8000)
