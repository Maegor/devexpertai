import uuid
from datetime import date, datetime

from pydantic import BaseModel

from models import LeadStatus


class LeadCreate(BaseModel):
    partner_id: uuid.UUID
    name: str
    email: str
    start_date: date
    end_date: date | None = None
    status: LeadStatus = LeadStatus.Active


class LeadUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: LeadStatus | None = None


class LeadResponse(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    name: str
    email: str
    start_date: date
    end_date: date | None
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
