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
from models.db_schemas.data_chunk import DataChunk
from models.db_schemas.asset import Asset
from models.PorjectDataModel import ProjectDataModel
from models.AssetsDataModel import AssetsDataModel
from models.ChunkDataModel import ChunkDataModel

logging.getLogger("uvicorn.error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["mini_rag", "Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):
    project_model = await ProjectDataModel.create_instance(
        db_client=request.app.mongo_conn
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
    asset_model = await AssetsDataModel.create_instance(
        db_client=request.app.mongo_conn
    )
    asset_resource = Asset(
        asset_project_id=str(project.id),
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
            "file_id": str(asset.id),
        },
    )


@data_router.post("/process/{project_id}")
async def process_file(
    request: Request, project_id: str, process_request: ProcessRequest
):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    chunk_model = await ChunkDataModel.create_instance(db_client=request.app.mongo_conn)
    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    project_model = await ProjectDataModel.create_instance(
        db_client=request.app.mongo_conn
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
    )
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": status.HTTP_400_BAD_REQUEST,
                "message": ResponseSignal.PROCESSING_FAILURE.value,
            },
        )
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project.id)
    inserted_count = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": status.HTTP_200_OK,
            "message": ResponseSignal.PROCESSING_SUCCESS.value,
            "file_id": file_id,
            "total_chunks": inserted_count,
        },
    )
