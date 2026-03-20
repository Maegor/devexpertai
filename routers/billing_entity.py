import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.billing_entity import BillingEntityCreate, BillingEntityUpdate, BillingEntityResponse
import repositories.billing_entity as repo

router = APIRouter(prefix="/billing-entities", tags=["billing-entities"])


@router.get("/", response_model=list[BillingEntityResponse])
async def list_billing_entities(db: AsyncSession = Depends(get_db)):
    return await repo.get_all(db)


@router.get("/partner/{partner_id}", response_model=list[BillingEntityResponse])
async def list_by_partner(partner_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await repo.get_by_partner(db, partner_id)


@router.get("/{entity_id}", response_model=BillingEntityResponse)
async def get_billing_entity(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    entity = await repo.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entidad de facturación no encontrada")
    return entity


@router.post("/", response_model=BillingEntityResponse, status_code=201)
async def create_billing_entity(data: BillingEntityCreate, db: AsyncSession = Depends(get_db)):
    return await repo.create(db, data)


@router.patch("/{entity_id}", response_model=BillingEntityResponse)
async def update_billing_entity(
    entity_id: uuid.UUID, data: BillingEntityUpdate, db: AsyncSession = Depends(get_db)
):
    entity = await repo.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entidad de facturación no encontrada")
    return await repo.update(db, entity, data)


@router.delete("/{entity_id}", status_code=204)
async def delete_billing_entity(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    entity = await repo.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entidad de facturación no encontrada")
    await repo.delete(db, entity)
