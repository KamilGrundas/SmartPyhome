import re
import uuid
from typing import Any

import wakeonlan
from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Computer,
    ComputerCreate,
    ComputerPublic,
    ComputersPublic,
    ComputerUpdate,
    Message,
)

router = APIRouter(prefix="/computers", tags=["computers"])

MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:\-]){5}([0-9A-Fa-f]{2})$")


def _validate_mac(mac: str) -> str:
    mac = mac.strip()
    if not MAC_RE.match(mac):
        raise HTTPException(
            status_code=422,
            detail="Invalid MAC address format. Use XX:XX:XX:XX:XX:XX",
        )
    return mac.upper().replace("-", ":")


@router.get("/", response_model=ComputersPublic)
def read_computers(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    count = session.exec(select(func.count()).select_from(Computer)).one()
    computers = session.exec(
        select(Computer).order_by(col(Computer.name)).offset(skip).limit(limit)
    ).all()
    return ComputersPublic(data=list(computers), count=count)


@router.get("/{id}", response_model=ComputerPublic)
def read_computer(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    computer = session.get(Computer, id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    return computer


@router.post("/", response_model=ComputerPublic)
def create_computer(
    *, session: SessionDep, current_user: CurrentUser, computer_in: ComputerCreate
) -> Any:
    computer_in.mac_address = _validate_mac(computer_in.mac_address)
    computer = Computer.model_validate(computer_in)
    session.add(computer)
    session.commit()
    session.refresh(computer)
    return computer


@router.put("/{id}", response_model=ComputerPublic)
def update_computer(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    computer_in: ComputerUpdate,
) -> Any:
    computer = session.get(Computer, id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    if computer_in.mac_address is not None:
        computer_in.mac_address = _validate_mac(computer_in.mac_address)
    update_dict = computer_in.model_dump(exclude_unset=True)
    computer.sqlmodel_update(update_dict)
    session.add(computer)
    session.commit()
    session.refresh(computer)
    return computer


@router.delete("/{id}")
def delete_computer(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    computer = session.get(Computer, id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    session.delete(computer)
    session.commit()
    return Message(message="Computer deleted successfully")


@router.post("/{id}/wake", response_model=Message)
def wake_computer(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    computer = session.get(Computer, id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    try:
        if computer.ip_address:
            wakeonlan.send_magic_packet(computer.mac_address, ip_address=computer.ip_address)
        else:
            wakeonlan.send_magic_packet(computer.mac_address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send magic packet: {e}")
    return Message(message=f"Magic packet sent to {computer.name}")
