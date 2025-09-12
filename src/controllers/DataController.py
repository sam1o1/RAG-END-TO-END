from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576  # 1 MB in bytes

    def validate_uploaded_file(self, file: UploadFile) -> bool:
        if file.content_type not in self.settings.ALLOWED_FILE_TYPES:
            return False , ResponseSignal.INVALID_FILE_TYPE.value
        if file.size > self.settings.ALLOWED_MAX_FILE_SIZE * self.size_scale:
            return False , ResponseSignal.FILE_EXCEEDS_MAX_SIZE.value
        return True , ResponseSignal.UPLOAD_SUCCESS.value
