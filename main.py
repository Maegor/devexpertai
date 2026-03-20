from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base
from routers import internal_user, partner, billing_entity


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="DevExpert AI", lifespan=lifespan)

app.include_router(internal_user.router)
app.include_router(partner.router)
app.include_router(billing_entity.router)


@app.get("/")
async def root():
    return {"status": "ok"}
