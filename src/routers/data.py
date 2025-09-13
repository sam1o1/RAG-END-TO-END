import os
import re
from urllib import response
from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
from models import ResponseSignal
import aiofiles
import logging

logging.getLogger("uvicorn.error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["mini_rag", "Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(
    project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)
):
    data_conroller = DataController()
    is_valid, signal = data_conroller.validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": status.HTTP_200_OK, "message": signal},
        )

    project_dir = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_conroller.generate_unique_filepath(
        orig_file_name=file.filename, project_id=project_id
    )
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while content := await file.read(
                app_settings.FILE_DEFAULT_CHUNK_SIZE
            ):  # Read file in chunks
                await f.write(content)
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": status.HTTP_400_BAD_REQUEST,
                "message": ResponseSignal.UPLOAD_FAILURE.value,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": status.HTTP_200_OK,
            "message": ResponseSignal.UPLOAD_SUCCESS.value,
            "file_name": file.filename,
            "file_type": file.content_type,
            "file_size": file.size * data_conroller.size_scale,
            "file_id": file_id,
        },
    )
