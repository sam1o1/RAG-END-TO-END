from calendar import c
from os import name

from annotated_types import T
from celery_app import celery_app, get_setup_utilities
from helpers.config import get_settings
import asyncio
import logging

# from time import sleep
from datetime import datetime
from models.db_schemas import DataChunk
from models.db_schemas import Asset
from models.PorjectDataModel import ProjectDataModel
from models.AssetsDataModel import AssetsDataModel
from models.ChunkDataModel import ChunkDataModel
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal

logger = logging.getLogger(
    "celery.task",
)


@celery_app.task(
    bind=True,
    name="tasks.file_processing.process_project_files",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def process_project_files(
    self,
    project_id: int,
    file_id: str,
    chunk_size: int,
    overlap_size: int,
    do_reset: int,
):
    return asyncio.run(
        _process_project_files(
            self, project_id, file_id, chunk_size, overlap_size, do_reset
        )
    )


async def _process_project_files(
    task_instance,
    project_id: int,
    file_id: str,
    chunk_size: int,
    overlap_size: int,
    do_reset: int,
):
    db_engine, db_client = None, None
    try:
        (
            db_engine,
            db_client,
            llm_provider_factory,
            vector_db_factory,
            generation_client,
            embedding_client,
            vector_db_client,
            template_parser,
        ) = await get_setup_utilities()
        chunk_model = await ChunkDataModel.create_instance(db_client=db_client)
        project_model = await ProjectDataModel.create_instance(db_client=db_client)
        project = await project_model.get_project_or_create_one(project_id=project_id)
        asset_model = await AssetsDataModel.create_instance(db_client=db_client)

        projects_files_ids = {}
        if file_id:
            asset_record = await asset_model.get_asset_by_id(
                asset_project_id=project.project_id, asset_name=file_id
            )
            if asset_record is None:
                # return JSONResponse(
                #     status_code=status.HTTP_400_BAD_REQUEST,
                #     content={
                #         "status": status.HTTP_400_BAD_REQUEST,
                #         "message": ResponseSignal.FILES_NOT_FOUND.value,
                #     },
                # )

                task_instance.update_state(
                    state="FAILURE",
                    meta={"message": ResponseSignal.FILES_NOT_FOUND.value},
                )
                raise Exception(ResponseSignal.FILES_NOT_FOUND.value)

            projects_files_ids = {asset_record.asset_id: str(asset_record.asset_name)}

        else:
            project_assets = await asset_model.get_all_project_assets(
                asset_project_id=project.project_id, asset_type="application/pdf"
            )
            projects_files_ids = {
                asset.asset_id: str(asset.asset_name) for asset in project_assets
            }
        if len(projects_files_ids) == 0:
            # return JSONResponse(
            #     status_code=status.HTTP_400_BAD_REQUEST,
            #     content={
            #         "status": status.HTTP_400_BAD_REQUEST,
            #         "message": ResponseSignal.FILES_NOT_FOUND.value,
            #     },
            # )
            task_instance.update_state(
                state="FAILURE",
                meta={"message": ResponseSignal.FILES_NOT_FOUND.value},
            )
            raise Exception(ResponseSignal.FILES_NOT_FOUND.value)
        process_controller = ProcessController(project_id=project_id)
        inserted_count = 0
        no_files = 0
        if do_reset == 1:
            _ = await chunk_model.delete_chunks_by_project_id(project.project_id)
        for _id, file_id in projects_files_ids.items():
            file_content = process_controller.get_file_content(file_id=file_id)
            if file_content is None or len(file_content) == 0:
                logger.error(f"Error processing file: {file_id}")
                continue

            file_chunks = process_controller.process_file_content(
                file_content=file_content,
                file_id=file_id,
                chunk_size=chunk_size,
                overlap_size=overlap_size,
            )
            if file_chunks is None or len(file_chunks) == 0:
                # return JSONResponse(
                #     status_code=status.HTTP_400_BAD_REQUEST,
                #     content={
                #         "status": status.HTTP_400_BAD_REQUEST,
                #         "message": ResponseSignal.PROCESSING_FAILURE.value,
                #     },
                # )
                logger.error(f"Error processing chunks for file: {file_id}")
                pass
            file_chunks_records = [
                DataChunk(
                    chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=i + 1,
                    chunk_project_id=project.project_id,
                    chunk_asset_id=_id,
                )
                for i, chunk in enumerate(file_chunks)
            ]

            inserted_count += await chunk_model.insert_many_chunks(
                chunks=file_chunks_records
            )
            no_files += 1
        task_instance.update_state(
            state="SUCCESS",
            meta={
                "message": ResponseSignal.PROCESSING_SUCCESS.value,
                "total_chunks": inserted_count,
                "total_files": no_files,
            },
        )

        return {
            "message": ResponseSignal.PROCESSING_SUCCESS.value,
            "total_chunks": inserted_count,
            "total_files": no_files,
        }
    except Exception as e:
        logger.error(f"Error processing project files: {e}")
        raise
    finally:
        try:
            await db_engine.dispose()
            if vector_db_client:
                vector_db_client.disconnect()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
