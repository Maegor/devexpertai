import uuid
from datetime import datetime

from pydantic import BaseModel

from models import PartnerCampaignStatus


class PartnerCampaignCreate(BaseModel):
    partner_id: uuid.UUID
    campaign_id: uuid.UUID
    coupon: str | None = None
    status: PartnerCampaignStatus
    start_date: datetime | None = None
    end_date: datetime | None = None


class PartnerCampaignUpdate(BaseModel):
    coupon: str | None = None
    status: PartnerCampaignStatus | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class PartnerCampaignResponse(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    campaign_id: uuid.UUID
    coupon: str | None
    status: PartnerCampaignStatus
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
