from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1.router import api_router
from app.core.milvus_client import milvus_client
from app.core.model_loader import get_model_loader
from app.services.generation_service import get_generation_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Visual RAG API...")

    try:
        logger.info("Connecting to Milvus...")
        milvus_client.connect()
        milvus_client.create_collection(dimension=128)
        logger.success("Milvus connected and collection ready")
    except Exception as exc:
        logger.opt(exception=exc).error("Failed to connect to Milvus")

    try:
        logger.info("Loading ColQwen2 model...")
        model_loader = get_model_loader()
        _ = model_loader.model
        logger.success("ColQwen2 model loaded successfully")
    except Exception as exc:
        logger.opt(exception=exc).error("Failed to load ColQwen2 model")

    yield

    logger.info("Shutting down Visual RAG API...")

    try:
        generation_service = get_generation_service()
        await generation_service.close()
        logger.info("Closed generation service")
    except Exception as exc:
        logger.opt(exception=exc).warning("Error closing generation service")

    try:
        milvus_client.disconnect()
        logger.info("Disconnected from Milvus")
    except Exception as exc:
        logger.opt(exception=exc).warning("Error disconnecting from Milvus")


app = FastAPI(
    title="Visual RAG API",
    description="Visual RAG with ColPali and Milvus",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Visual RAG API"}


@app.get("/health")
def health():
    milvus_connected = False
    model_loaded = False

    try:
        client = milvus_client._get_client()
        if client:
            milvus_connected = True
    except Exception:
        pass

    try:
        model_loader = get_model_loader()
        model_loaded = model_loader.is_loaded()
    except Exception:
        pass

    overall_status = "healthy" if (milvus_connected and model_loaded) else "degraded"

    return {
        "status": overall_status,
        "milvus": milvus_connected,
        "model": model_loaded,
    }
