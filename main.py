from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from database import engine, Base
from routers import internal_user, partner, billing_entity, web, invoice
from routers import admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="DevExpert AI", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key="change-me-in-production-use-env-var")

app.include_router(internal_user.router)
app.include_router(partner.router)
app.include_router(billing_entity.router)
app.include_router(invoice.router)
app.include_router(web.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"status": "ok"}
