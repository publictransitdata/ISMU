from app.error_codes import ErrorCodes
from utils.singleton_decorator import singleton
from utils.error_handler import set_error_and_raise
from .config_info import SystemConfig, CurrentSystemChosenConfiguraion, TripInfo


@singleton
class ConfigManager:
    def __init__(self):
        self._config = SystemConfig()
        self._current_config = CurrentSystemChosenConfiguraion()

    def _convert_value(self, key: str, value: str):
        if key in {
            "show_start_and_end_stops",
            "force_short_names",
            "show_route_on_stop_board",
        }:
            return value.lower() == "true"

        if key in {"baudrate", "bits", "parity", "stop"}:
            try:
                return int(value)
            except ValueError:
                set_error_and_raise(ErrorCodes.CONFIG_INVALID_VALUE)

        return value

    def load_config(self, config_path: str) -> None:
        try:
            with open(config_path, "r") as file:
                lines = file.readlines()
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
                if key in {"line", "destination_number", "destination", "stop_board_telegram"}:
                    converted = value if value else None
                else:
                    converted = self._convert_value(key, value)
                setattr(self._config, key, converted)
            else:
                set_error_and_raise(ErrorCodes.CONFIG_UNKNOWN_KEY)

    @property
    def config(self):
        return self._config

    def update_current_configuration(self, route_number, trip, no_line_telegram=False):
        self._current_config.route_number = route_number
        self._current_config.trip = TripInfo.trip_from_dict(trip)
        self._current_config.no_line_telegram = no_line_telegram
        self._current_config.isUpdated = True

    def get_current_configuration(self):
        return self._current_config

    def get_telegram_types(self):
        keys = ["line", "destination_number", "destination", "stop_board_telegram"]
        return {getattr(self._config, k) for k in keys if getattr(self._config, k)}
