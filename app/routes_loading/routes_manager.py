from .singleton_decorator import singleton
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
        self.import_routes_txt(routes_path)
        self._route_list = self.build_route_list()
        print("Routes was loaded")

    def append_route(self, number: str):
        rec = {"t": "route", "n": number}
        with open(DB_PATH, "a") as f:
            f.write(json.dumps(rec) + "\n")

    def append_direction(
        self, route_number: str, d_id: str, p_id: str, full_name: str, short_name=None
    ):
        rec = {"t": "dir", "rn": route_number, "d": d_id, "p": p_id, "f": full_name}
        if short_name:
            rec["s"] = short_name
        with open(DB_PATH, "a") as f:
            f.write(json.dumps(rec) + "\n")

    def import_routes_txt(self, path_txt):
        with open(path_txt, "rb") as fh:
            current_route = None

            for raw in fh:
                line = raw.decode("utf-8").strip()
                if not line:
                    continue

                if line.startswith("|"):
                    try:
                        num_line = next(fh).decode("utf-8").strip()
                    except StopIteration:
                        break

                    if "#" in num_line:
                        num_line = num_line.split("#", 1)[0].strip()
                    if "-" in num_line:
                        num_line = num_line.replace("-", "").strip()

                    current_route = num_line or None
                    if current_route:
                        self.append_route(current_route)
                    continue

                parts = [p.strip() for p in line.split(",")]
                if len(parts) not in (3, 4) or not current_route:
                    continue

                d_id, p_id = parts[0], parts[1]
                full_name = parts[2].split("^")
                short_name = None

                if len(parts) == 4:
                    short_name = parts[3].split("^")

                self.append_direction(current_route, d_id, p_id, full_name, short_name)

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
            return []

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
