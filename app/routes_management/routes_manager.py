from app.error_codes import ErrorCodes
from utils.singleton_decorator import singleton
from utils.error_handler import set_error_and_raise
import os
import ujson as json

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
            set_error_and_raise(ErrorCodes.ROUTES_FILE_NOT_FOUND)

        try:
            self._route_list = self.build_route_list()
            print("Routes was loaded")
            return
        except Exception:
            pass

        try:
            self.refresh_db(ROUTES_PATH)
            self._route_list = self.build_route_list()
            print("Routes was loaded after refresh db")
        except Exception as e:
            set_error_and_raise(ErrorCodes.ROUTES_DB_OPEN_FAILED, e)

    def refresh_db(self, routes_path: str) -> None:
        """
        Args:
            routes_path: The path to the routes.txt file.
        """
        try:
            os.remove(DB_PATH)
        except OSError:
            pass

        self.import_routes_from_txt(routes_path)

    def append_route(
        self,
        route_id: int,
        number: str,
        no_line_telegram: bool = False,
        note: str | None = None,
    ) -> None:
        try:
            rec = {"t": "route", "id": route_id, "n": number}
            if no_line_telegram:
                rec["nlt"] = True
            if note:
                rec["note"] = note
            with open(DB_PATH, "a") as f:
                f.write(json.dumps(rec) + "\n")
        except OSError as e:
            set_error_and_raise(ErrorCodes.ROUTES_DB_WRITE_FAILED, e)

    def append_direction(
        self,
        route_id: int,
        route_number: str,
        d_id: str,
        p_id: str,
        full_name: str,
        short_name=None,
    ) -> None:
        try:
            rec = {
                "t": "dir",
                "rid": route_id,
                "rn": route_number,
                "d": d_id,
                "p": p_id,
                "f": full_name,
            }
            if short_name:
                rec["s"] = short_name
            with open(DB_PATH, "a") as f:
                f.write(json.dumps(rec) + "\n")
        except OSError as e:
            set_error_and_raise(ErrorCodes.ROUTES_DB_WRITE_FAILED, e)

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
                            set_error_and_raise(ErrorCodes.ROUTES_EMPTY_ROUTE_NUMBER)

                        current_route = num_line
                        current_route_id = next_route_id
                        self.append_route(
                            current_route_id, current_route, no_line_telegram, note
                        )
                        next_route_id += 1
                        has_routes = True
                        expecting_route_after_separator = False
                        continue

                    if current_route is None or current_route_id is None:
                        set_error_and_raise(ErrorCodes.ROUTES_DIRECTION_WITHOUT_ROUTE)
                        return

                    parts = [p.strip() for p in line.split(",")]

                    if len(parts) not in (3, 4):
                        set_error_and_raise(
                            ErrorCodes.ROUTES_DIRECTION_WRONG_PARTS_COUNT
                        )

                    d_id, p_id, full_name_str = parts[0], parts[1], parts[2]

                    if not d_id or not p_id:
                        set_error_and_raise(ErrorCodes.ROUTES_DIRECTION_EMPTY_ID)

                    full_name = full_name_str.split("^")

                    short_name = None
                    if len(parts) == 4:
                        short_name_str = parts[3]
                        if "^" not in short_name_str:
                            set_error_and_raise(
                                ErrorCodes.ROUTES_SHORT_NAME_NO_SEPARATOR
                            )
                        short_name = short_name_str.split("^")
                        if len(short_name) < 2:
                            set_error_and_raise(
                                ErrorCodes.ROUTES_SHORT_NAME_TOO_FEW_PARTS
                            )

                    self.append_direction(
                        current_route_id,
                        current_route,
                        d_id,
                        p_id,
                        full_name,
                        short_name,
                    )

                if not has_routes:
                    set_error_and_raise(ErrorCodes.ROUTES_NO_ROUTES_FOUND)

        except OSError as e:
            if e.args[0] == 2:
                set_error_and_raise(ErrorCodes.ROUTES_FILE_NOT_FOUND, e)
            else:
                set_error_and_raise(ErrorCodes.ROUTES_FILE_OPEN_FAILED, e)

    def build_route_list(self):
        routes_list = []

        try:
            with open(DB_PATH, "r") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("t") == "route":
                        routes_list.append(
                            {
                                "id": rec.get("id"),
                                "n": rec.get("n"),
                                "nlt": rec.get("nlt", False),
                                "note": rec.get("note"),
                            }
                        )
        except OSError as e:
            raise RuntimeError(f"Failed to open routes DB: {e}")

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
        route_number = route_info["n"]
        no_line_telegram = route_info.get("nlt", False)
        note = route_info.get("note")
        dirs = []

        try:
            with open(DB_PATH, "r") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("t") == "dir" and rec.get("rid") == route_id:
                        dirs.append(
                            {
                                "trip_id": rec.get("d", ""),
                                "point_id": rec.get("p", ""),
                                "full_name": rec.get("f", ""),
                                "short_name": rec.get("s", None),
                            }
                        )
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
