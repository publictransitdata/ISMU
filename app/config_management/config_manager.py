from app.error_codes import ErrorCodes
from utils.error_handler import set_error_and_raise
from utils.singleton_decorator import singleton

from .config_info import CurrentRouteTripSelection, SystemConfig, TripInfo


@singleton
class ConfigManager:
    def __init__(self):
        self._config = SystemConfig()
        self._current_selection = CurrentRouteTripSelection()

    def _convert_value(self, key: str, value: str):
        if key in {
            "show_start_and_end_stops",
            "force_short_names",
            "show_info_on_stop_board",
        }:
            if value.lower() not in ("true", "false"):
                set_error_and_raise(
                    ErrorCodes.CONFIG_INVALID_VALUE,
                    ValueError(f"Expected 'true' or 'false' for {key}, got '{value}'"),
                    show_message=True,
                )
            return value.lower() == "true"

        if key in {"baudrate", "bits", "parity", "stop"}:
            try:
                return int(value)
            except ValueError:
                set_error_and_raise(
                    ErrorCodes.CONFIG_INVALID_VALUE,
                    ValueError(f"Could not convert {key}={value} to int"),
                    show_message=True,
                )

        return value

    def load_config(self, config_path: str) -> None:
        try:
            with open(config_path, "r") as file:
                content = file.read()

                if not content.strip():
                    set_error_and_raise(
                        ErrorCodes.CONFIG_FILE_EMPTY,
                        Exception("Config file is empty"),
                        show_message=True,
                    )

                lines = content.splitlines()
                self._parse_config(lines)
                print("Config was loaded.")
        except OSError as e:
            # errno 2 = ENOENT (file not found)
            if e.args[0] == 2:
                set_error_and_raise(ErrorCodes.CONFIG_FILE_NOT_FOUND, e)
            else:
                set_error_and_raise(ErrorCodes.CONFIG_IO_ERROR, e)

    def _parse_config(self, lines: list[str]) -> None:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "=" not in line:
                set_error_and_raise(ErrorCodes.CONFIG_NO_EQUALS_SIGN)

            key, value = map(str.strip, line.split("=", 1))
            if hasattr(self._config, key):
                if key in {
                    "line_telegram",
                    "destination_number_telegram",
                    "destination_telegram",
                    "stop_board_telegram",
                }:
                    converted = value if value else None
                else:
                    converted = self._convert_value(key, value)
                setattr(self._config, key, converted)
            else:
                set_error_and_raise(ErrorCodes.CONFIG_UNKNOWN_KEY)

    @property
    def config(self):
        return self._config

    def update_current_selection(self, route_number, trip, no_line_telegram=False):
        self._current_selection.route_number = route_number
        self._current_selection.trip = TripInfo.trip_from_dict(trip)
        self._current_selection.no_line_telegram = no_line_telegram
        self._current_selection.is_updated = True

    def get_current_selection(self):
        return self._current_selection

    def get_telegram_types(self):
        keys = [
            "line_telegram",
            "destination_number_telegram",
            "destination_telegram",
            "stop_board_telegram",
        ]
        return {getattr(self._config, k) for k in keys if getattr(self._config, k)}
