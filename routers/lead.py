import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import repositories.lead as lead_repo
from schemas.lead import LeadCreate, LeadUpdate, LeadResponse

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("/", response_model=list[LeadResponse])
async def list_leads(db: AsyncSession = Depends(get_db)):
    return await lead_repo.get_all(db)


@router.get("/partner/{partner_id}", response_model=list[LeadResponse])
async def list_leads_by_partner(partner_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await lead_repo.get_by_partner(db, partner_id)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    lead = await lead_repo.get_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/", response_model=LeadResponse, status_code=201)
async def create_lead(data: LeadCreate, db: AsyncSession = Depends(get_db)):
    return await lead_repo.create(db, data)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: uuid.UUID, data: LeadUpdate, db: AsyncSession = Depends(get_db)):
    lead = await lead_repo.get_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return await lead_repo.update(db, lead, data)


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    lead = await lead_repo.get_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await lead_repo.delete(db, lead)
