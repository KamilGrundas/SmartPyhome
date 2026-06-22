import hashlib
import hmac
import time
import uuid
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.models import (
    AccessCard,
    AccessCardCreate,
    AccessCardPublic,
    AccessCardsPublic,
    AccessCardUpdate,
    AccessGroup,
    AccessGroupCreate,
    AccessGroupPublic,
    AccessGroupsPublic,
    AccessGroupUpdate,
    AccessPoint,
    AccessPointCreate,
    AccessPointPublic,
    AccessPointsPublic,
    AccessPointUpdate,
    CardAccessPoint,
    CardGroup,
    GroupAccessPoint,
    Message,
)

router = APIRouter(prefix="/access", tags=["access"])

# ── Helpers ──────────────────────────────────────────────────────────────────


def _verify_hmac(timestamp: str, uid: str, gate: str, signature: str) -> None:
    """Verify the HMAC-SHA256 signature from the ESP32.

    Raises HTTPException 403 if the signature is invalid or the timestamp is
    outside the allowed window.
    """
    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        raise HTTPException(status_code=403, detail="Invalid timestamp")

    # ts=0 means ESP32 SNTP hasn't synced yet — skip the window check but still
    # verify the signature so the secret is still validated.
    if ts != 0:
        now = int(time.time())
        if ts > now + 60 or ts < now - 300:
            raise HTTPException(status_code=403, detail="Request timestamp out of window")

    message = f"{timestamp}{uid}{gate}"
    expected = hmac.new(
        settings.RFID_HMAC_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")


def _card_public(session: Any, card: AccessCard) -> AccessCardPublic:
    point_ids = [
        row.point_id
        for row in session.exec(
            select(CardAccessPoint).where(CardAccessPoint.card_id == card.id)
        ).all()
    ]
    group_ids = [
        row.group_id
        for row in session.exec(
            select(CardGroup).where(CardGroup.card_id == card.id)
        ).all()
    ]
    return AccessCardPublic(
        **card.model_dump(),
        access_point_ids=point_ids,
        group_ids=group_ids,
    )


def _group_public(session: Any, group: AccessGroup) -> AccessGroupPublic:
    point_ids = [
        row.point_id
        for row in session.exec(
            select(GroupAccessPoint).where(GroupAccessPoint.group_id == group.id)
        ).all()
    ]
    return AccessGroupPublic(
        **group.model_dump(),
        access_point_ids=point_ids,
    )


class AccessCheckRequest(BaseModel):
    uid: str
    gate: str


# ── ESP32 HMAC endpoint (public) ──────────────────────────────────────────────


@router.post("")
def check_access(
    body: AccessCheckRequest,
    session: SessionDep,
    x_timestamp: str = Header(..., alias="X-Timestamp"),
    x_signature: str = Header(..., alias="X-Signature"),
) -> dict[str, bool]:
    """Verify an RFID access request from the ESP32 reader."""
    uid = body.uid
    gate = body.gate

    if not uid or not gate:
        raise HTTPException(status_code=422, detail="uid and gate are required")

    _verify_hmac(x_timestamp, uid, gate, x_signature)

    # Look up the card
    card = session.exec(select(AccessCard).where(AccessCard.uid == uid)).first()
    if not card or not card.is_active:
        raise HTTPException(status_code=403, detail="Access denied")

    # Find the access point by name
    access_point = session.exec(
        select(AccessPoint).where(AccessPoint.name == gate)
    ).first()
    if not access_point:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check direct card → point assignment
    direct = session.exec(
        select(CardAccessPoint).where(
            CardAccessPoint.card_id == card.id,
            CardAccessPoint.point_id == access_point.id,
        )
    ).first()
    if direct:
        return {"granted": True}

    # Check via group: card → group → point
    card_groups = session.exec(
        select(CardGroup).where(CardGroup.card_id == card.id)
    ).all()
    group_ids = [cg.group_id for cg in card_groups]

    if group_ids:
        group_point = session.exec(
            select(GroupAccessPoint).where(
                col(GroupAccessPoint.group_id).in_(group_ids),
                GroupAccessPoint.point_id == access_point.id,
            )
        ).first()
        if group_point:
            return {"granted": True}

    raise HTTPException(status_code=403, detail="Access denied")


# ── Access Points ─────────────────────────────────────────────────────────────


@router.get("/points", response_model=AccessPointsPublic, dependencies=[])
def list_access_points(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    count = session.exec(select(func.count()).select_from(AccessPoint)).one()
    points = session.exec(
        select(AccessPoint).order_by(col(AccessPoint.name)).offset(skip).limit(limit)
    ).all()
    return AccessPointsPublic(data=list(points), count=count)


@router.post("/points", response_model=AccessPointPublic)
def create_access_point(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    point_in: AccessPointCreate,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    point = AccessPoint.model_validate(point_in)
    session.add(point)
    session.commit()
    session.refresh(point)
    return point


@router.patch("/points/{point_id}", response_model=AccessPointPublic)
def update_access_point(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    point_id: uuid.UUID,
    point_in: AccessPointUpdate,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    point = session.get(AccessPoint, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Access point not found")
    update_data = point_in.model_dump(exclude_unset=True)
    point.sqlmodel_update(update_data)
    session.add(point)
    session.commit()
    session.refresh(point)
    return point


@router.delete("/points/{point_id}")
def delete_access_point(
    session: SessionDep,
    current_user: CurrentUser,
    point_id: uuid.UUID,
) -> Message:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    point = session.get(AccessPoint, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Access point not found")
    session.delete(point)
    session.commit()
    return Message(message="Access point deleted successfully")


# ── Access Groups ─────────────────────────────────────────────────────────────


@router.get("/groups", response_model=AccessGroupsPublic)
def list_access_groups(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    count = session.exec(select(func.count()).select_from(AccessGroup)).one()
    groups = session.exec(
        select(AccessGroup).order_by(col(AccessGroup.name)).offset(skip).limit(limit)
    ).all()
    return AccessGroupsPublic(
        data=[_group_public(session, g) for g in groups],
        count=count,
    )


@router.post("/groups", response_model=AccessGroupPublic)
def create_access_group(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    group_in: AccessGroupCreate,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    group = AccessGroup.model_validate(group_in)
    session.add(group)
    session.commit()
    session.refresh(group)
    return _group_public(session, group)


@router.patch("/groups/{group_id}", response_model=AccessGroupPublic)
def update_access_group(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    group_id: uuid.UUID,
    group_in: AccessGroupUpdate,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    group = session.get(AccessGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Access group not found")
    update_data = group_in.model_dump(exclude_unset=True)
    group.sqlmodel_update(update_data)
    session.add(group)
    session.commit()
    session.refresh(group)
    return _group_public(session, group)


@router.delete("/groups/{group_id}")
def delete_access_group(
    session: SessionDep,
    current_user: CurrentUser,
    group_id: uuid.UUID,
) -> Message:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    group = session.get(AccessGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Access group not found")
    session.delete(group)
    session.commit()
    return Message(message="Access group deleted successfully")


@router.post("/groups/{group_id}/points/{point_id}", response_model=AccessGroupPublic)
def add_point_to_group(
    session: SessionDep,
    current_user: CurrentUser,
    group_id: uuid.UUID,
    point_id: uuid.UUID,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    group = session.get(AccessGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Access group not found")
    point = session.get(AccessPoint, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Access point not found")
    existing = session.exec(
        select(GroupAccessPoint).where(
            GroupAccessPoint.group_id == group_id,
            GroupAccessPoint.point_id == point_id,
        )
    ).first()
    if not existing:
        link = GroupAccessPoint(group_id=group_id, point_id=point_id)
        session.add(link)
        session.commit()
    return _group_public(session, group)


@router.delete("/groups/{group_id}/points/{point_id}", response_model=AccessGroupPublic)
def remove_point_from_group(
    session: SessionDep,
    current_user: CurrentUser,
    group_id: uuid.UUID,
    point_id: uuid.UUID,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    group = session.get(AccessGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Access group not found")
    link = session.exec(
        select(GroupAccessPoint).where(
            GroupAccessPoint.group_id == group_id,
            GroupAccessPoint.point_id == point_id,
        )
    ).first()
    if link:
        session.delete(link)
        session.commit()
    return _group_public(session, group)


# ── Access Cards ──────────────────────────────────────────────────────────────


@router.get("/cards", response_model=AccessCardsPublic)
def list_access_cards(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    count = session.exec(select(func.count()).select_from(AccessCard)).one()
    cards = session.exec(
        select(AccessCard).order_by(col(AccessCard.label)).offset(skip).limit(limit)
    ).all()
    return AccessCardsPublic(
        data=[_card_public(session, c) for c in cards],
        count=count,
    )


@router.post("/cards", response_model=AccessCardPublic)
def create_access_card(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    card_in: AccessCardCreate,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    existing = session.exec(
        select(AccessCard).where(AccessCard.uid == card_in.uid)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="A card with this UID already exists")
    card = AccessCard.model_validate(card_in)
    session.add(card)
    session.commit()
    session.refresh(card)
    return _card_public(session, card)


@router.patch("/cards/{card_id}", response_model=AccessCardPublic)
def update_access_card(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    card_id: uuid.UUID,
    card_in: AccessCardUpdate,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    card = session.get(AccessCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Access card not found")
    if card_in.uid is not None and card_in.uid != card.uid:
        conflict = session.exec(
            select(AccessCard).where(AccessCard.uid == card_in.uid)
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail="A card with this UID already exists")
    update_data = card_in.model_dump(exclude_unset=True)
    card.sqlmodel_update(update_data)
    session.add(card)
    session.commit()
    session.refresh(card)
    return _card_public(session, card)


@router.delete("/cards/{card_id}")
def delete_access_card(
    session: SessionDep,
    current_user: CurrentUser,
    card_id: uuid.UUID,
) -> Message:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    card = session.get(AccessCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Access card not found")
    session.delete(card)
    session.commit()
    return Message(message="Access card deleted successfully")


@router.post("/cards/{card_id}/points/{point_id}", response_model=AccessCardPublic)
def add_point_to_card(
    session: SessionDep,
    current_user: CurrentUser,
    card_id: uuid.UUID,
    point_id: uuid.UUID,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    card = session.get(AccessCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Access card not found")
    point = session.get(AccessPoint, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Access point not found")
    existing = session.exec(
        select(CardAccessPoint).where(
            CardAccessPoint.card_id == card_id,
            CardAccessPoint.point_id == point_id,
        )
    ).first()
    if not existing:
        link = CardAccessPoint(card_id=card_id, point_id=point_id)
        session.add(link)
        session.commit()
    return _card_public(session, card)


@router.delete("/cards/{card_id}/points/{point_id}", response_model=AccessCardPublic)
def remove_point_from_card(
    session: SessionDep,
    current_user: CurrentUser,
    card_id: uuid.UUID,
    point_id: uuid.UUID,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    card = session.get(AccessCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Access card not found")
    link = session.exec(
        select(CardAccessPoint).where(
            CardAccessPoint.card_id == card_id,
            CardAccessPoint.point_id == point_id,
        )
    ).first()
    if link:
        session.delete(link)
        session.commit()
    return _card_public(session, card)


@router.post("/cards/{card_id}/groups/{group_id}", response_model=AccessCardPublic)
def add_card_to_group(
    session: SessionDep,
    current_user: CurrentUser,
    card_id: uuid.UUID,
    group_id: uuid.UUID,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    card = session.get(AccessCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Access card not found")
    group = session.get(AccessGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Access group not found")
    existing = session.exec(
        select(CardGroup).where(
            CardGroup.card_id == card_id,
            CardGroup.group_id == group_id,
        )
    ).first()
    if not existing:
        link = CardGroup(card_id=card_id, group_id=group_id)
        session.add(link)
        session.commit()
    return _card_public(session, card)


@router.delete("/cards/{card_id}/groups/{group_id}", response_model=AccessCardPublic)
def remove_card_from_group(
    session: SessionDep,
    current_user: CurrentUser,
    card_id: uuid.UUID,
    group_id: uuid.UUID,
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    card = session.get(AccessCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Access card not found")
    link = session.exec(
        select(CardGroup).where(
            CardGroup.card_id == card_id,
            CardGroup.group_id == group_id,
        )
    ).first()
    if link:
        session.delete(link)
        session.commit()
    return _card_public(session, card)
