import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.partner import PartnerCreate, PartnerUpdate, PartnerResponse
import repositories.partner as repo

router = APIRouter(prefix="/partners", tags=["partners"])


@router.get("/", response_model=list[PartnerResponse])
async def list_partners(db: AsyncSession = Depends(get_db)):
    return await repo.get_all(db)


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(partner_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    partner = await repo.get_by_id(db, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
    return partner


@router.post("/", response_model=PartnerResponse, status_code=201)
async def create_partner(data: PartnerCreate, db: AsyncSession = Depends(get_db)):
    existing = await repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    return await repo.create(db, data)


@router.patch("/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    partner_id: uuid.UUID, data: PartnerUpdate, db: AsyncSession = Depends(get_db)
):
    partner = await repo.get_by_id(db, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
    return await repo.update(db, partner, data)


@router.delete("/{partner_id}", status_code=204)
async def delete_partner(partner_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    partner = await repo.get_by_id(db, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner no encontrado")
    await repo.delete(db, partner)
