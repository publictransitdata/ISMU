import gc
import os

import ujson as json

from app.error_codes import ErrorCodes
from utils.error_handler import set_error_and_raise
from utils.file_checker import check_config_content_file
from utils.singleton_decorator import singleton

from .config_info import SystemConfig

CONFIG_PATH = "/config/config.json"


@singleton
class ConfigManager:
    def __init__(self):
        self.config = SystemConfig()

    def load_config(self) -> None:
        try:
            os.stat(CONFIG_PATH)
        except OSError:
            set_error_and_raise(ErrorCodes.CONFIG_FILE_NOT_FOUND, raise_exception=False)
            return

        errors = check_config_content_file(CONFIG_PATH)
        if errors:
            set_error_and_raise(
                ErrorCodes.CONFIG_CHECKER_FAILED, exception=errors[0], show_message=True, raise_exception=False
            )
            return

        try:
            with open(CONFIG_PATH) as file:
                try:
                    data = json.load(file)
                    for key, value in data.items():
                        setattr(self.config, key, value)
                except Exception:
                    set_error_and_raise(ErrorCodes.CONFIG_JSON_LOAD_ERROR, raise_exception=False)
        except OSError:
            set_error_and_raise(ErrorCodes.CONFIG_FILE_OPEN_FAILED, raise_exception=False)

        print("Config was loaded")
        gc.collect()
        return

    def get_telegram_types(self):
        keys = [
            "line_telegram",
            "destination_number_telegram",
            "destination_telegram",
            "stop_board_telegram",
        ]
        return {getattr(self.config, k) for k in keys if getattr(self.config, k)}
