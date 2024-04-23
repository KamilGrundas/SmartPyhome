import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from src.routes import cases, camera
from src.scripts.cases import get_case_prices
from fastapi.templating import Jinja2Templates
from camera_service import port_connection
from src.conf.config import settings
import subprocess

IP = settings.ip
templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.include_router(cases.router, prefix="")
app.include_router(camera.router, prefix="")


def run_camera_server(filename):
    process = subprocess.Popen(['python', filename])


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    cameras_number = len(port_connection.read_ports_from_file("camera_service/ports.bin"))
    context: dict = {"cameras_number": cameras_number}
    print(cameras_number)
    return templates.TemplateResponse('index.html', {"request": request, "cameras_number": cameras_number})


@app.post("/load_case_prices/")
async def load_case_prices():
    await get_case_prices()

if __name__ == "__main__":
    run_camera_server("camera_service/camera_server.py")
    uvicorn.run(app, host=IP, port=8000)
