from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os
import re
from .ProjectController import ProjectController


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576  # 1 MB in bytes

    def validate_uploaded_file(self, file: UploadFile) -> bool:
        if file.content_type not in self.settings.ALLOWED_FILE_TYPES:
            return False, ResponseSignal.INVALID_FILE_TYPE.value
        if file.size > self.settings.ALLOWED_MAX_FILE_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_EXCEEDS_MAX_SIZE.value
        return True, ResponseSignal.UPLOAD_SUCCESS.value

    def generate_unique_filepath(self, orig_file_name: str, project_id: str):

        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)

        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path, random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r"[^\w.]", "", orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
