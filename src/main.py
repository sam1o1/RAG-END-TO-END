from fastapi import APIRouter, FastAPI
from routers import data, base, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.mongo_db = app.mongo_conn[settings.MONGO_DB_NAME]
    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_factory = VectorDBProviderFactory(settings)
    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MOELL_ID)
    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE,
    )
    app.vector_db_client = vector_db_factory.create(proivder=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    app.mongo_conn.close()
    app.vector_db_client.disconnect()


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
