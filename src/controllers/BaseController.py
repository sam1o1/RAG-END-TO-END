from helpers.config import get_settings, Settings


class BaseController:
    def __init__(self):
        self.settings: Settings = get_settings()
