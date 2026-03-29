import gc
import os

import ujson as json

from app.error_codes import ErrorCodes
from utils.custom_error import CustomError
from utils.error_handler import set_error_and_raise
from utils.singleton_decorator import singleton

ROUTES_PATH = "/config/routes.ndjson"


@singleton
class RoutesManager:
    def __init__(self):
        self._route_list = []
        self._file_path = ROUTES_PATH

    def load_routes(self) -> None:
        try:
            os.stat(ROUTES_PATH)
        except OSError:
            set_error_and_raise(ErrorCodes.ROUTES_FILE_NOT_FOUND, raise_exception=False)
            return

        try:
            self._route_list = self.build_route_list()
            print("Routes was loaded")
            gc.collect()
            return
        except (ValueError, RuntimeError):
            pass

    def remove_routes(self) -> None:
        try:
            os.remove(ROUTES_PATH)
            self._route_list = []
        except OSError as err:
            if err.args[0] == 2:
                self._route_list = []
            else:
                raise CustomError(ErrorCodes.ROUTES_FILE_DELETE_FAILED, str(err)) from err

    def build_route_list(self):
        routes_list = []

        try:
            with open(ROUTES_PATH) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if "id" in rec:
                        routes_list.append({
                            "id": rec.get("id"),
                            "r": rec.get("r"),
                            "nlt": rec.get("nlt", False),
                            "note": rec.get("note"),
                        })
        except OSError as err:
            raise RuntimeError(f"Failed to open routes file: {err}") from err

        if not routes_list:
            raise ValueError("Routes file is empty")

        return routes_list

    def get_routes_labels(self):
        labels = {}

        try:
            with open(ROUTES_PATH) as f:
                for line in f:
                    try:
                        record = json.loads(line)
                    except Exception:
                        continue
                    if "did" not in record or record["did"] in labels:
                        continue
                    labels[record["did"]] = record.get("s") or record.get("f", "")
                    if len(labels) == len(self._route_list):
                        break
        except OSError:
            pass

        return labels

    def get_route_by_index(self, index: int):
        if index < 0 or index >= len(self._route_list):
            return {
                "route_number": "",
                "dirs": [],
                "no_line_telegram": False,
                "note": None,
            }

        route_info = self._route_list[index]
        route_id = route_info["id"]
        route_number = route_info["r"]
        no_line_telegram = route_info.get("nlt", False)
        note = route_info.get("note")
        dirs = []

        try:
            with open(ROUTES_PATH) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("did") == route_id:
                        dirs.append({
                            "trip_id": rec.get("d", ""),
                            "point_id": rec.get("p", ""),
                            "full_name": rec.get("f", ""),
                            "short_name": rec.get("s", None),
                        })
        except OSError:
            pass
        return {
            "route_number": route_number,
            "dirs": dirs,
            "no_line_telegram": no_line_telegram,
            "note": note,
        }

    def get_length_of_routes(self) -> int:
        return len(self._route_list)

    def get_length_of_trips(self, route_idx: int) -> int:
        route = self.get_route_by_index(route_idx)
        return len(route.get("dirs", [])) if route else 0
