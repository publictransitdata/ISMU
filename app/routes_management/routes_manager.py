import gc
import os

import ujson as json

from app.error_codes import ErrorCodes
from utils.custom_error import CustomError
from utils.error_handler import set_error_and_raise
from utils.singleton_decorator import singleton

DB_PATH = "/config/routes_db.ndjson"
ROUTES_PATH = "/config/routes.txt"


@singleton
class RoutesManager:
    def __init__(self):
        self._route_list = []
        self._db_file_path = DB_PATH

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

        try:
            self.refresh_db(ROUTES_PATH)
        except CustomError as err:
            self.remove_db()
            set_error_and_raise(err.error_code, err, show_message=True, raise_exception=False)
            return

        try:
            self._route_list = self.build_route_list()
            print("Routes was loaded after refresh db")
            gc.collect()
        except (ValueError, RuntimeError) as err:
            set_error_and_raise(ErrorCodes.ROUTES_DB_OPEN_FAILED, err, raise_exception=False)

    def refresh_db(self, routes_path: str) -> None:
        """
        Args:
            routes_path: The path to the routes.txt file.
        """
        self.remove_db()
        self.import_routes_from_txt(routes_path)

    def remove_db(self) -> None:
        try:
            os.remove(DB_PATH)
            self._route_list = []
        except OSError as err:
            if err.args[0] == 2:
                self._route_list = []
            else:
                raise CustomError(ErrorCodes.ROUTES_DB_DELETE_FAILED, str(err)) from err

    def append_route(
        self,
        route_id: int,
        number: str,
        no_line_telegram: bool = False,
        note: str | None = None,
    ) -> None:
        try:
            rec = {"id": route_id, "r": number}
            if no_line_telegram:
                rec["nlt"] = True
            if note:
                rec["note"] = note
            with open(DB_PATH, "a") as f:
                line = json.dumps(rec).replace(": ", ":").replace(", ", ",")
                f.write(line + "\n")
        except OSError as err:
            raise CustomError(ErrorCodes.ROUTES_DB_WRITE_FAILED, str(err)) from err

    def append_direction(
        self,
        route_id: int,
        d_id: str,
        p_id: str,
        full_name: str,
        short_name=None,
    ) -> None:
        try:
            rec = {
                "rid": route_id,
                "d": d_id,
                "p": p_id,
                "f": full_name,
            }
            if short_name:
                rec["s"] = short_name
            with open(DB_PATH, "a") as f:
                line = json.dumps(rec).replace(": ", ":").replace(", ", ",")
                f.write(line + "\n")
        except OSError as err:
            raise CustomError(ErrorCodes.ROUTES_DB_WRITE_FAILED, str(err)) from err

    def import_routes_from_txt(self, path_txt):
        next_route_id = 0
        try:
            with open(path_txt, "rb") as fh:
                current_route = None
                current_route_id = None
                line_number = 0
                has_routes = False
                expecting_route_after_separator = False

                for raw in fh:
                    line_number += 1
                    line = raw.decode("utf-8").strip()

                    if not line:
                        continue

                    if line.startswith("|"):
                        expecting_route_after_separator = True
                        current_route = None
                        current_route_id = None
                        continue

                    if expecting_route_after_separator:
                        note = None
                        if "#" in line:
                            num_line, note_part = line.split("#", 1)
                            num_line = num_line.strip()
                            note = note_part.strip() if note_part.strip() else None
                        else:
                            num_line = line

                        no_line_telegram = num_line.endswith("-")
                        if no_line_telegram:
                            num_line = num_line[:-1].strip()

                        if not num_line:
                            raise CustomError(
                                ErrorCodes.ROUTES_EMPTY_ROUTE_NUMBER,
                                ErrorCodes.get_message(ErrorCodes.ROUTES_EMPTY_ROUTE_NUMBER)
                                + "."
                                + f"Рядок:{line_number}",
                            )

                        current_route = num_line
                        current_route_id = next_route_id
                        self.append_route(current_route_id, current_route, no_line_telegram, note)
                        next_route_id += 1
                        has_routes = True
                        expecting_route_after_separator = False
                        continue

                    if current_route is None or current_route_id is None:
                        raise CustomError(
                            ErrorCodes.ROUTES_DIRECTION_WITHOUT_ROUTE,
                            ErrorCodes.get_message(ErrorCodes.ROUTES_DIRECTION_WITHOUT_ROUTE)
                            + "."
                            + f"Рядок:{line_number}",
                        )
                        return

                    parts = [p.strip() for p in line.split(",")]

                    if len(parts) not in (3, 4):
                        raise CustomError(
                            ErrorCodes.ROUTES_DIRECTION_WRONG_PARTS_COUNT,
                            ErrorCodes.get_message(ErrorCodes.DS003_ERROR) + "." + f"Рядок:{line_number}",
                        )

                    d_id, p_id, full_name_str = parts[0], parts[1], parts[2]

                    if not d_id or not p_id:
                        raise CustomError(
                            ErrorCodes.ROUTES_DIRECTION_EMPTY_ID,
                            ErrorCodes.get_message(ErrorCodes.ROUTES_DIRECTION_EMPTY_ID) + "." + f"Рядок:{line_number}",
                        )

                    full_name = full_name_str.split("^")

                    short_name = None
                    if len(parts) == 4:
                        short_name_str = parts[3]
                        if "^" not in short_name_str:
                            raise CustomError(
                                ErrorCodes.ROUTES_SHORT_NAME_NO_SEPARATOR,
                                ErrorCodes.get_message(ErrorCodes.ROUTES_SHORT_NAME_NO_SEPARATOR)
                                + "."
                                + f"Рядок:{line_number}",
                            )
                        short_name = short_name_str.split("^")
                        if len(short_name) < 2:
                            raise CustomError(
                                ErrorCodes.ROUTES_SHORT_NAME_TOO_FEW_PARTS,
                                ErrorCodes.get_message(ErrorCodes.ROUTES_SHORT_NAME_TOO_FEW_PARTS)
                                + "."
                                + f"Рядок:{line_number}",
                            )

                    self.append_direction(
                        current_route_id,
                        d_id,
                        p_id,
                        full_name,
                        short_name,
                    )

                if not has_routes:
                    raise CustomError(
                        ErrorCodes.ROUTES_NO_ROUTES_FOUND,
                        ErrorCodes.get_message(ErrorCodes.ROUTES_NO_ROUTES_FOUND) + "." + f"Рядок:{line_number}",
                    )

        except OSError as err:
            if err.args[0] == 2:
                raise CustomError(ErrorCodes.ROUTES_FILE_NOT_FOUND, str(err)) from err
            else:
                raise CustomError(ErrorCodes.ROUTES_FILE_OPEN_FAILED, str(err)) from err

    def build_route_list(self):
        routes_list = []

        try:
            with open(DB_PATH) as f:
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
            raise RuntimeError(f"Failed to open routes DB: {err}") from err

        if not routes_list:
            raise ValueError("Routes DB is empty")

        return routes_list

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
            with open(DB_PATH) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("rid") == route_id:
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
