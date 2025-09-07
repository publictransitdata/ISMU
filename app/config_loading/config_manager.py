from .singleton_decorator import singleton
from .config_info import SystemConfig


@singleton
class ConfigManager:
    def __init__(self):
        self._config = SystemConfig()

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
