from utils.singleton_decorator import singleton
from .config_info import SystemConfig, CurrentSystemChosenConfiguraion, TripInfo


@singleton
class ConfigManager:
    def __init__(self):
        self._config = SystemConfig()
        self._current_config = CurrentSystemChosenConfiguraion()

    def _convert_value(self, key: str, value: str):
        if key in {
            "display_start_and_end_stops",
            "force_short_names",
            "show_route_on_stop_board",
        }:
            return value.lower() == "true"

        if key in {"baudrate", "bits", "parity", "stop"}:
            try:
                return int(value)
            except ValueError:
                print(f"Warning: Could not convert {key}={value} to int")
                return getattr(self._config, key)

        return value

    def load_config(self, config_path: str) -> None:
        """
        Args:
            config_path: The path to the config.txt file.
        """
        try:
            with open(config_path, "r") as file:
                lines = file.readlines()
                self._parse_config(lines)
                print("Config was loaded.")
        except Exception as e:
            from app.gui_management import ScreenConfig, ScreenStates

            screen_config = ScreenConfig()
            screen_config.current_screen = ScreenStates.ERROR_SCREEN
            screen_config.error_message = f"Error while loading config: {e}"

    def _parse_config(self, lines: list[str]) -> None:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "=" not in line:
                print(f"Invalid config line: {line}")
                raise ValueError(f"Invalid config line: {line}")

            key, value = map(str.strip, line.split("=", 1))
            if hasattr(self._config, key):
                setattr(self._config, key, self._convert_value(key, value))
            else:
                print(f"Unknown config key: {key}")
                raise ValueError(f"Unknown config key: {key}")

    @property
    def config(self):
        return self._config

    def update_current_configuration(self, route_number, trip):
        self._current_config.route_number = route_number
        self._current_config.trip = TripInfo.trip_from_dict(trip)

    def get_current_configuration(self):
        return self._current_config

    def get_telegram_types(self):
        keys = ["line", "destination_number", "destination", "stop_board_telegram"]
        return [getattr(self._config, k) for k in keys]
