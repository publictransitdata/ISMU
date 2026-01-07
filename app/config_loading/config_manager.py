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
            "display_route_on_stop_board",
        }:
            return value.lower() == "true"
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
            print(f"Error while loading config: {e}")

    def _parse_config(self, lines: list[str]) -> None:
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                print(f"Skipping invalid line: {line}")
                continue

            key, value = map(str.strip, line.split("=", 1))
            if hasattr(self._config, key):
                setattr(self._config, key, self._convert_value(key, value))
            else:
                print(f"Unknown config key: {key}")

    @property
    def config(self):
        return self._config

    def update_current_configuration(self, route_number, trip):
        self._current_config.route_number = route_number
        self._current_config.trip = TripInfo.trip_from_dict(trip)

    def get_current_configuration(self):
        return self._current_config

    def get_telegram_types(self):
        keys = ["line", "destination_number", "destination", "stop_display_telegram"]
        return [getattr(self._config, k) for k in keys]
