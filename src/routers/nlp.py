from gettext import dpgettext
from re import template
from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from httpx import request
from openai import project
from routers.schemas.nlp import PushRequest, SearcRequest
from models.PorjectDataModel import ProjectDataModel
from models.ChunkDataModel import ChunkDataModel
from controllers import NLPController
from models import ResponseSignal
import logging

from stores.llm.templates import template_parser


logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["mini_rag", "nlp"],
)


@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    project_data_model = await ProjectDataModel.create_instance(
        db_client=request.app.mongo_conn
    )
    project = await project_data_model.get_project_or_create_one(project_id=project_id)
    chunk_model = await ChunkDataModel.create_instance(db_client=request.app.mongo_conn)

    if not project:
        JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignal.PROJECT_NOT_FOUND.value},
        )
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0
    while has_records:

        page_chunks = await chunk_model.get_project_chunks(
            project_id=project.id, page_no=page_no
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
            do_reset=push_request.do_reset,
            chunks_ids=chunk_ids,
        )
        if not is_inserted:
            JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": ResponseSignal.INSERT_INTO_DB_ERROR.value,
                },
            )
        inserted_items_count += len(page_chunks)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseSignal.INSERT_INTO_DB_SUCCESS.value,
            "inserted items count": inserted_items_count,
        },
    )


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    project_data_model = await ProjectDataModel.create_instance(
        db_client=request.app.mongo_conn
    )
    project = await project_data_model.get_project_or_create_one(project_id=project_id)
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    collection_info = nlp_controller.vector_db_collection_info(project=project)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseSignal.VECTOR_DB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info,
        },
    )


@nlp_router.get("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearcRequest):
    project_data_model = await ProjectDataModel.create_instance(
        db_client=request.app.mongo_conn
    )
    project = await project_data_model.get_project_or_create_one(project_id=project_id)
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    results = nlp_controller.search_db_collection(
        project=project, text=search_request.text, limit=search_request.limit
    )

    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponseSignal.VECTOR_DB_SEARCH_ERROR.value,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseSignal.VECTOR_DB_SEARCH_SUCCESS.value,
            "results": [result.dict() for result in results],
        },
    )


@nlp_router.get("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: str, search_request: SearcRequest):
    project_data_model = await ProjectDataModel.create_instance(
        db_client=request.app.mongo_conn
    )
    project = await project_data_model.get_project_or_create_one(project_id=project_id)
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
        template_parser=request.app.template_parser,
    )
    answer, full_prompt, chat_history = nlp_controller.answer_rag_questions(
        project=project, query=search_request.text, limit=search_request.limit
    )

    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignal.RAG_ANSWER_ERROR.value},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history,
        },
    )
