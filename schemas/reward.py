import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class RewardCreate(BaseModel):
    partner_id: uuid.UUID
    transaction_date: datetime
    product_code: str
    customer_id: uuid.UUID | None = None
    customer_email: str | None = None
    amount: Decimal
    currency: str
    reward_type: str


class RewardUpdate(BaseModel):
    transaction_date: datetime | None = None
    product_code: str | None = None
    customer_id: uuid.UUID | None = None
    customer_email: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    reward_type: str | None = None


class RewardResponse(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    transaction_date: datetime
    product_code: str
    customer_id: uuid.UUID | None
    customer_email: str | None
    amount: Decimal
    currency: str
    reward_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
