import uuid
from datetime import datetime

from pydantic import BaseModel

from models import CampaignStatus


class CampaignCreate(BaseModel):
    name: str
    description: str
    coupon: str
    status: CampaignStatus
    start_date: datetime | None = None
    end_date: datetime | None = None


class CampaignUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    coupon: str | None = None
    status: CampaignStatus | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class CampaignResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    coupon: str
    status: CampaignStatus
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
