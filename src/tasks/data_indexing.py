from celery_app import celery_app, get_setup_utilities
import asyncio
import logging
from models.PorjectDataModel import ProjectDataModel
from models.ChunkDataModel import ChunkDataModel
from controllers import NLPController
from models import ResponseSignal

logger = logging.getLogger(
    "celery.task",
)


@celery_app.task(
    bind=True,
    name="tasks.data_indexing.index_data_content",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def index_data_content(self, project_id: int, do_reset: int):

    return asyncio.run(_index_data_content(self, project_id, do_reset))


async def _index_data_content(task_instance, project_id: int, do_reset: int):
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
        project_data_model = await ProjectDataModel.create_instance(db_client=db_client)
        project = await project_data_model.get_project_or_create_one(
            project_id=project_id
        )
        chunk_model = await ChunkDataModel.create_instance(db_client=db_client)

        if not project:
            task_instance.update_state(
                state="FAILURE",
                meta={"message": ResponseSignal.PROJECT_NOT_FOUND.value},
            )
            raise Exception(ResponseSignal.PROJECT_NOT_FOUND.value)
        nlp_controller = NLPController(
            vector_db_client=vector_db_client,
            generation_client=generation_client,
            embedding_client=embedding_client,
            template_parser=template_parser,
        )

        has_records = True
        page_no = 1
        inserted_items_count = 0
        idx = 0
        while has_records:

            page_chunks = await chunk_model.get_project_chunks(
                project_id=project.project_id, page_no=page_no
            )
            if len(page_chunks):
                page_no += 1
            if not page_chunks or len(page_chunks) == 0:
                has_records = False
                break
            chunk_ids = list(range(idx, idx + len(page_chunks)))
            idx += len(page_chunks)
            is_inserted = nlp_controller.index_into_vector_db(
                project=project,
                chunks=page_chunks,
                do_reset=do_reset,
                chunks_ids=chunk_ids,
            )
            if not is_inserted:
                task_instance.update_state(
                    state="FAILURE",
                    meta={"message": ResponseSignal.INSERT_INTO_DB_ERROR.value},
                )
                raise Exception(ResponseSignal.INSERT_INTO_DB_ERROR.value)

            inserted_items_count += len(page_chunks)
            task_instance(
                state="SUCCESS",
                meta={
                    "message": ResponseSignal.INSERT_INTO_DB_SUCCESS.value,
                    "inserted items count": inserted_items_count,
                },
            )

        return {
            "message": ResponseSignal.INSERT_INTO_DB_SUCCESS.value,
            "inserted items count": inserted_items_count,
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
