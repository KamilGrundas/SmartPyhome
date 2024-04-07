from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from src.repository.camera import video_generator

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("/stream/")
async def stream():
    try:
        return StreamingResponse(
            content=video_generator(),
            media_type='multipart/x-mixed-replace; boundary=frame',
        )
    except HTTPException:
        return HTMLResponse(status_code=500, content="<h1>Błąd połączenia</h1><p>Serwer wideo jest niedostępny.</p>")


