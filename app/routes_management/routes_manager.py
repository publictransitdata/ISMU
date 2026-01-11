from app.error_codes import ErrorCodes
from utils.singleton_decorator import singleton
from utils.error_handler import set_error_and_raise
import os
import ujson as json

DB_PATH = "/config/routes_db.ndjson"


@singleton
class RoutesManager:
    def __init__(self):
        self._route_doc_ids = None
        self._route_list = []
        self._db_file_path = DB_PATH

    def load_routes(self, routes_path: str) -> None:
        """
        Args:
            routes_path: The path to the routes.txt file.
        """
        try:
            os.remove(DB_PATH)
        except OSError:
            pass

        self.import_routes_from_txt(routes_path)
        self._route_list = self.build_route_list()
        print("Routes was loaded")

    def append_route(self, number: str):
        try:
            rec = {"t": "route", "n": number}
            with open(DB_PATH, "a") as f:
                f.write(json.dumps(rec) + "\n")
        except OSError:
            set_error_and_raise(ErrorCodes.ROUTES_DB_WRITE_FAILED)

    def append_direction(
        self, route_number: str, d_id: str, p_id: str, full_name: str, short_name=None
    ):
        try:
            rec = {"t": "dir", "rn": route_number, "d": d_id, "p": p_id, "f": full_name}
            if short_name:
                rec["s"] = short_name
            with open(DB_PATH, "a") as f:
                f.write(json.dumps(rec) + "\n")
        except OSError:
            set_error_and_raise(ErrorCodes.ROUTES_DB_WRITE_FAILED)

    def import_routes_from_txt(self, path_txt):
        try:
            with open(path_txt, "rb") as fh:
                current_route = None
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
                        continue

                    if expecting_route_after_separator:
                        if "#" in line:
                            num_line = line.split("#", 1)[0].strip()
                        else:
                            num_line = line

                        if num_line.endswith("-"):
                            num_line = num_line[:-1].strip()

                        if not num_line:
                            set_error_and_raise(ErrorCodes.ROUTES_EMPTY_ROUTE_NUMBER)

                        current_route = num_line
                        self.append_route(current_route)
                        has_routes = True
                        expecting_route_after_separator = False
                        continue

                    if not current_route:
                        set_error_and_raise(ErrorCodes.ROUTES_DIRECTION_WITHOUT_ROUTE)

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
                        current_route, d_id, p_id, full_name, short_name
                    )

                if not has_routes:
                    set_error_and_raise(ErrorCodes.ROUTES_NO_ROUTES_FOUND)

        except OSError as e:
            if e.args[0] == 2:
                set_error_and_raise(ErrorCodes.ROUTES_FILE_NOT_FOUND, e)
            else:
                set_error_and_raise(ErrorCodes.ROUTES_DB_OPEN_FAILED, e)

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
                        n = rec.get("n")
                        if n and n not in routes_list:
                            routes_list.append(n)
        except OSError:
            set_error_and_raise(ErrorCodes.ROUTES_DB_OPEN_FAILED)

        return routes_list

    def get_route_by_index(self, index: int):
        route_number = self._route_list[index]
        dirs = []
        try:
            with open(DB_PATH, "r") as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("t") == "dir" and rec.get("rn") == route_number:
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
        return {"route_number": route_number, "dirs": dirs}

    def get_length_of_routes(self) -> int:
        return len(self._route_list)

    def get_length_of_trips(self, route_idx: int) -> int:
        route = self.get_route_by_index(route_idx)
        return len(route.get("dirs", [])) if route else 0
