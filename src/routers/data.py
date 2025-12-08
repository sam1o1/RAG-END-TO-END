import os
import re
from urllib import response
from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import aiofiles
import logging

from .schemas.data import ProcessRequest
from models.db_schemas import DataChunk
from models.db_schemas import Asset
from models.PorjectDataModel import ProjectDataModel
from models.AssetsDataModel import AssetsDataModel
from models.ChunkDataModel import ChunkDataModel
from tasks.file_processing import process_project_files

logging.getLogger("uvicorn.error")
logger = logging.getLogger(__name__)
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["mini_rag", "Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(
    request: Request,
    project_id: int,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):
    project_model = await ProjectDataModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)
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
    asset_model = await AssetsDataModel.create_instance(db_client=request.app.db_client)
    asset_resource = Asset(
        asset_project_id=project.project_id,
        asset_type=file.content_type,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
    )

    asset = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": status.HTTP_200_OK,
            "message": ResponseSignal.UPLOAD_SUCCESS.value,
            "file_name": file.filename,
            "file_type": file.content_type,
            "file_size": file.size * data_conroller.size_scale,
            "file_id": str(asset.asset_id),
        },
    )


@data_router.post("/process/{project_id}")
async def process_file(
    request: Request, project_id: int, process_request: ProcessRequest
):
    # file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    task = process_project_files.delay(
        project_id, process_request.file_id, chunk_size, overlap_size, do_reset
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": status.HTTP_200_OK,
            "message": "Successfully started processing files",
            "task_id": task.id,
        },
    )
