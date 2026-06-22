import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    username: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    username: str | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Computer models

class ComputerBase(SQLModel):
    name: str = Field(max_length=255)
    mac_address: str = Field(
        max_length=17,
        description="MAC address in XX:XX:XX:XX:XX:XX format",
    )
    ip_address: str | None = Field(default=None, max_length=45)
    description: str | None = Field(default=None, max_length=255)


class ComputerCreate(ComputerBase):
    pass


class ComputerUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    mac_address: str | None = Field(default=None, max_length=17)
    ip_address: str | None = Field(default=None, max_length=45)
    description: str | None = Field(default=None, max_length=255)


class Computer(ComputerBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class ComputerPublic(ComputerBase):
    id: uuid.UUID
    created_at: datetime | None = None


class ComputersPublic(SQLModel):
    data: list[ComputerPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore[assignment]


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# RFID Access models

# Link tables
class CardGroup(SQLModel, table=True):
    card_id: uuid.UUID = Field(foreign_key="accesscard.id", primary_key=True, ondelete="CASCADE")
    group_id: uuid.UUID = Field(foreign_key="accessgroup.id", primary_key=True, ondelete="CASCADE")


class CardAccessPoint(SQLModel, table=True):
    card_id: uuid.UUID = Field(foreign_key="accesscard.id", primary_key=True, ondelete="CASCADE")
    point_id: uuid.UUID = Field(foreign_key="accesspoint.id", primary_key=True, ondelete="CASCADE")


class GroupAccessPoint(SQLModel, table=True):
    group_id: uuid.UUID = Field(foreign_key="accessgroup.id", primary_key=True, ondelete="CASCADE")
    point_id: uuid.UUID = Field(foreign_key="accesspoint.id", primary_key=True, ondelete="CASCADE")


class AccessPointBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)


class AccessPointCreate(AccessPointBase):
    pass


class AccessPointUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class AccessPoint(AccessPointBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class AccessPointPublic(AccessPointBase):
    id: uuid.UUID
    created_at: datetime | None = None


class AccessPointsPublic(SQLModel):
    data: list[AccessPointPublic]
    count: int


class AccessGroupBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)


class AccessGroupCreate(AccessGroupBase):
    pass


class AccessGroupUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class AccessGroup(AccessGroupBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class AccessGroupPublic(AccessGroupBase):
    id: uuid.UUID
    created_at: datetime | None = None
    access_point_ids: list[uuid.UUID] = []


class AccessGroupsPublic(SQLModel):
    data: list[AccessGroupPublic]
    count: int


class AccessCardBase(SQLModel):
    uid: str = Field(unique=True, max_length=50, description="RFID card UID e.g. AA:BB:CC:DD")
    label: str = Field(max_length=255)
    is_active: bool = True
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", ondelete="SET NULL")


class AccessCardCreate(AccessCardBase):
    pass


class AccessCardUpdate(SQLModel):
    uid: str | None = Field(default=None, max_length=50)
    label: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    user_id: uuid.UUID | None = None


class AccessCard(AccessCardBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class AccessCardPublic(AccessCardBase):
    id: uuid.UUID
    created_at: datetime | None = None
    access_point_ids: list[uuid.UUID] = []
    group_ids: list[uuid.UUID] = []


class AccessCardsPublic(SQLModel):
    data: list[AccessCardPublic]
    count: int


class AccessLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    uid: str = Field(max_length=50)
    label: str | None = Field(default=None, max_length=255)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", ondelete="SET NULL")
    gate_name: str = Field(max_length=255)
    granted: bool


class AccessLogPublic(SQLModel):
    id: uuid.UUID
    timestamp: datetime
    uid: str
    label: str | None = None
    username: str | None = None
    gate_name: str
    granted: bool


class AccessLogsPublic(SQLModel):
    data: list[AccessLogPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
