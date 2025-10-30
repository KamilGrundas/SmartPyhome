import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import (
    StreamingResponse,
)
from sqlmodel import select, func

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
)
from app.models import Camera, CameraPublic, CamerasPublic, CameraCreate
from app.services.camera_manager import CameraManager

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("/", response_model=CamerasPublic)
def read_cameras(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    count = session.exec(select(func.count()).select_from(Camera)).one()
    items = session.exec(select(Camera).offset(skip).limit(limit)).all()
    return CamerasPublic(
        data=[CameraPublic.model_validate(i) for i in items], count=count
    )


@router.get("/{id}", response_model=CameraPublic)
def read_camera(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    cam = session.get(Camera, id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return CameraPublic.model_validate(cam)


@router.post("/", response_model=CameraPublic, status_code=status.HTTP_201_CREATED)
def create_camera(
    *,
    session: SessionDep,
    current_user=Depends(get_current_active_superuser),
    camera_in: CameraCreate,
) -> Any:
    """
    Create new camera (admin only).
    """
    exists = session.exec(select(Camera).where(Camera.name == camera_in.name)).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Camera with this name already exists",
        )

    camera = Camera.model_validate(camera_in)
    session.add(camera)
    session.commit()
    session.refresh(camera)
    return CameraPublic.model_validate(camera)


@router.get("/{id}/video")
def stream_camera(
    request: Request,
    session: SessionDep,
    id: uuid.UUID,
    token: str | None = Query(default=None),
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = get_current_user(session=session, token=token)
    if not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )

    cam = session.get(Camera, id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    mgr: CameraManager = request.app.state.camera_manager
    runtime = mgr.ensure(cam.name, cam.ip_address)  # <-- KLUCZ = NAZWA

    boundary = "frame"

    def gen():
        while True:
            jpg = runtime.get_jpeg(80)
            if jpg is None:
                time.sleep(0.05)
                continue
            yield (
                b"--" + boundary.encode() + b"\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: "
                + str(len(jpg)).encode()
                + b"\r\n\r\n"
                + jpg
                + b"\r\n"
            )

    return StreamingResponse(
        gen(), media_type=f"multipart/x-mixed-replace; boundary={boundary}"
    )
