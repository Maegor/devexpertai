from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from database import engine, Base
from routers import internal_user, partner, billing_entity, web, invoice, reward
from routers import admin
from routers import partner_portal
from routers import sales


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="DevExpert AI", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="change-me-in-production-use-env-var")

app.include_router(internal_user.router, prefix="/api")
app.include_router(partner.router, prefix="/api")
app.include_router(billing_entity.router, prefix="/api")
app.include_router(invoice.router, prefix="/api")
app.include_router(reward.router, prefix="/api")
app.include_router(web.router)
app.include_router(admin.router)
app.include_router(partner_portal.router)
app.include_router(sales.router)


@app.get("/")
async def root():
    return {"status": "ok"}
