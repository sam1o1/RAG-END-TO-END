from enum import Enum


class ResponseSignal(Enum):
    FILE_EXCEEDS_MAX_SIZE = "File exceeds maximum allowed size."
    INVALID_FILE_TYPE = "Invalid file type."
    FILE_VALID = "File is valid."
    UPLOAD_SUCCESS = "File uploaded successfully."
    UPLOAD_FAILURE = "File upload failed."
