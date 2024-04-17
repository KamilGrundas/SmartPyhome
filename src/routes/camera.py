from fastapi import APIRouter
from src.repository.camera import get_video_stream
from fastapi.responses import StreamingResponse
from camera_service import port_connection

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("/video/{camera_id}")
async def video_endpoint(camera_id: int):
    ports = port_connection.read_ports_from_file("camera_service/ports.bin")
    port = ports[camera_id]
    return StreamingResponse(get_video_stream(port + 1000), media_type="multipart/x-mixed-replace; boundary=frame")


@router.get("/get_active_camera_ports")
async def load_case_prices():
    return port_connection.read_ports_from_file("camera_service/ports.bin")
