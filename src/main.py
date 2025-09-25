from fastapi import APIRouter, FastAPI
from routers import data, base
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.mongo_db = app.mongo_conn[settings.MONGO_DB_NAME]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongo_conn.close()


app.include_router(base.base_router)
app.include_router(data.data_router)
