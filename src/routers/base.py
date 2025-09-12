from email.mime import base
from fastapi import FastAPI, APIRouter, Depends, status
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["mini_rag"],
)


@base_router.get("/health")
async def welcome(app_settings: Settings = Depends(get_settings)):
    # settings = get_settings()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": f"Healthy 🟢 ... {status.HTTP_200_OK}",
            "message": f"Welcome to {app_settings.APP_NAME}!",
            "version": app_settings.APP_VERSION,
        },
    )
