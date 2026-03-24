import gc

from app.error_codes import ErrorCodes
from utils.custom_error import CustomError
from utils.error_handler import set_error_and_raise
from utils.singleton_decorator import singleton

from .config_info import SystemConfig


@singleton
class ConfigManager:
    def __init__(self):
        self.config = SystemConfig()

    def _convert_value(self, key: str, value: str):
        if key in {
            "show_start_and_end_stops",
            "force_short_names",
            "show_info_on_stop_board",
        }:
            if value.lower() not in ("true", "false"):
                raise CustomError(
                    ErrorCodes.CONFIG_INVALID_VALUE,
                    f"Expected 'true' or 'false' for {key}, got '{value}'",
                )
            return value.lower() == "true"

        if key in {"baudrate", "bits", "parity", "stop"}:
            try:
                return int(value)
            except ValueError as err:
                raise CustomError(
                    ErrorCodes.CONFIG_INVALID_VALUE,
                    f"Could not convert {key}={value} to int",
                ) from err
        return value

    def load_config(self, config_path: str) -> None:
        try:
            with open(config_path) as file:
                content = file.read()

                if not content.strip():
                    raise CustomError(ErrorCodes.CONFIG_FILE_EMPTY, "Config file is empty")

                lines = content.splitlines()
                self._parse_config(lines)
                print("Config was loaded.")
                gc.collect()
        except CustomError as err:
            set_error_and_raise(err.error_code, err, show_message=True, raise_exception=False)
        except OSError as err:
            # errno 2 = ENOENT (file not found)
            if err.args[0] == 2:
                set_error_and_raise(ErrorCodes.CONFIG_FILE_NOT_FOUND, err, raise_exception=False)
            else:
                set_error_and_raise(ErrorCodes.CONFIG_IO_ERROR, err, raise_exception=False)

    def _parse_config(self, lines: list[str]) -> None:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "=" not in line:
                raise CustomError(ErrorCodes.CONFIG_NO_EQUALS_SIGN, f"Missing '=' in line: {line}")

            key, value = map(str.strip, line.split("=", 1))
            if hasattr(self.config, key):
                if key in {
                    "line_telegram",
                    "destination_number_telegram",
                    "destination_telegram",
                    "stop_board_telegram",
                }:
                    converted = value if value else None
                else:
                    converted = self._convert_value(key, value)
                setattr(self.config, key, converted)
            else:
                raise CustomError(ErrorCodes.CONFIG_UNKNOWN_KEY, f"Unknown key: {key}")

    def get_telegram_types(self):
        keys = [
            "line_telegram",
            "destination_number_telegram",
            "destination_telegram",
            "stop_board_telegram",
        ]
        return {getattr(self.config, k) for k in keys if getattr(self.config, k)}
