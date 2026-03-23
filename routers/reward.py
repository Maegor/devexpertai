import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories import reward as reward_repo
from schemas.reward import RewardCreate, RewardUpdate, RewardResponse

router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.get("/", response_model=list[RewardResponse])
async def list_rewards(db: AsyncSession = Depends(get_db)):
    return await reward_repo.get_all(db)


@router.get("/partner/{partner_id}", response_model=list[RewardResponse])
async def list_by_partner(partner_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await reward_repo.get_by_partner(db, partner_id)


@router.get("/{reward_id}", response_model=RewardResponse)
async def get_reward(reward_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    reward = await reward_repo.get_by_id(db, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward no encontrado")
    return reward


@router.post("/", response_model=RewardResponse, status_code=status.HTTP_201_CREATED)
async def create_reward(data: RewardCreate, db: AsyncSession = Depends(get_db)):
    return await reward_repo.create(db, data)


@router.put("/{reward_id}", response_model=RewardResponse)
async def update_reward(reward_id: uuid.UUID, data: RewardUpdate, db: AsyncSession = Depends(get_db)):
    reward = await reward_repo.get_by_id(db, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward no encontrado")
    return await reward_repo.update(db, reward, data)


@router.delete("/{reward_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reward(reward_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    reward = await reward_repo.get_by_id(db, reward_id)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward no encontrado")
    await reward_repo.delete(db, reward)
