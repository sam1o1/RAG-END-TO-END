from enum import Enum
from http.client import PROCESSING


class ResponseSignal(Enum):
    FILE_EXCEEDS_MAX_SIZE = "File exceeds maximum allowed size."
    INVALID_FILE_TYPE = "Invalid file type."
    FILE_VALID = "File is valid."
    UPLOAD_SUCCESS = "File uploaded successfully."
    UPLOAD_FAILURE = "File upload failed."
    PROCESSING_FAILURE = "File processing failed."
    PROCESSING_SUCCESS = "File processed successfully."
    FILES_NOT_FOUND = "No files found."
    PROJECT_NOT_FOUND = "Project Not Found"
    INSERT_INTO_DB_ERROR = " insert error into db"
    INSERT_INTO_DB_SUCCESS = " insert success into db"
    VECTOR_DB_COLLECTION_RETRIEVED = "Vector database collection retrieved"
    VECTOR_DB_SEARCH_ERROR = "SEARCH ERROR"
    VECTOR_DB_SEARCH_SUCCESS = "SEARCH successfulL"
    RAG_ANSWER_ERROR = "rag answer error"
    RAG_ANSWER_SUCCESS = "rag answer success"
    DATA_PUSH_TASK_READY = "data push task is ready"
