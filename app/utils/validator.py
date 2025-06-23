import os
import json
import re

REQUIRED_CONFIG_KEYS = {
    "ibis_interface",
    "line",
    "dest_num",
    "destination",
    "display_start_and_dist",
    "forse_short_names",
    "stop_display",
    "rt_on_stop_disp",
    "ap_pswd",
}

BOOLEAN_KEYS = {
    "display_start_and_dist",
    "forse_short_names",
    "rt_on_stop_disp",
}


class ValidationError(Exception):
    """Raised when validation of a file fails."""

    pass


class FileValidator:
    @staticmethod
    def validate_config_file(path: str) -> dict:
        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except OSError:
            raise ValidationError(f"Missing config file: {path}")

        config = {}
        for line in lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if "=" not in line:
                raise ValidationError(f"Invalid line in config: {line}")
            key, value = map(str.strip, line.split("=", 1))
            config[key] = value

        missing_keys = REQUIRED_CONFIG_KEYS - set(config.keys())
        if missing_keys:
            raise ValidationError(
                f"Missing required keys in config: {', '.join(missing_keys)}"
            )

        for key in BOOLEAN_KEYS:
            if config[key] not in ("true", "false"):
                raise ValidationError(f"Invalid boolean value for {key}: {config[key]}")

        return config
