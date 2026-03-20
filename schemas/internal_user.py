import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from models import InternalRole


class InternalUserCreate(BaseModel):
    name: str
    email: EmailStr
    password_hash: str
    totp_secret: str | None = None
    mfa_enabled: bool = False
    role: InternalRole = InternalRole.Sales
    is_active: bool = True


class InternalUserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    totp_secret: str | None = None
    mfa_enabled: bool | None = None
    role: InternalRole | None = None
    is_active: bool | None = None


class InternalUserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    mfa_enabled: bool
    role: InternalRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
