from fastapi import APIRouter, WebSocket
from src.repository.camera import video_stream

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.websocket("/camera_1")
async def video_feed(websocket: WebSocket):
    await video_stream(websocket)
