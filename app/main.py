# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session as SQLSession

from app.core.config import settings
from app.api.main import api_router
from app.services.camera_manager import CameraManager
from app.models import Camera
from app.core.db import engine

templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.camera_manager = CameraManager()

    try:
        with SQLSession(engine) as session:
            cams = session.exec(select(Camera)).all()
            mgr: CameraManager = app.state.camera_manager
            for cam in cams:
                try:
                    mgr.ensure(cam.name, cam.ip_address)
                except Exception:
                    pass
    except Exception:
        pass

    yield

    try:
        mgr: CameraManager = app.state.camera_manager
        mgr.stop_all()
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "api_prefix": settings.API_V1_STR}
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "api_prefix": settings.API_V1_STR}
    )


@app.get("/logout")
def logout():
    # tylko redirect – JS na stronie wyczyści localStorage
    return RedirectResponse("/login", status_code=302)
