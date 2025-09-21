from .singleton_decorator import singleton
from tinydb import where
from app.db_manager import DBManager
import gc


@singleton
class RoutesManager:
    def __init__(self):
        self._db_manager = DBManager()
        self._route_doc_ids = None
        self._route_count = None

    def load_routes(self, routes_path: str) -> None:
        """
        Args:
            routes_path: The path to the routes.txt file.
        """
        with open(routes_path, "rb") as f:
            try:
                self._parse_routes_and_store(f)
                self._build_index()
                print("Routes was loaded")
            except ValueError:
                print("Error while loading routes")

    def _parse_routes_and_store(self, lines: list[str]) -> None:
        current_route_number = None
        current_trips = []

        def flush_route(db, route_number: str, dirs: list):
            if not route_number:
                return
            t = db.table("routes")
            doc = t.get(where("route_number") == route_number)
            if doc:
                t.update({"dirs": dirs}, doc_ids=[doc.doc_id])
            else:
                t.insert({"route_number": route_number, "dirs": dirs})

        for line in lines:
            line = line.decode("utf-8").strip()
            if not line:
                continue

            if line.startswith("|"):
                self._db_manager.with_db(
                    lambda db: flush_route(db, current_route_number, current_trips)
                )
                current_trips = []

                try:
                    next_line = next(lines).decode("utf-8").strip()
                except StopIteration:
                    print("Warning: Unexpected end of input after '|'")
                    current_route_number = None
                    break

                if "#" in next_line:
                    next_line = next_line.split("#", 1)[0].strip()
                if "-" in next_line:
                    next_line = next_line.replace("-", "").strip()

                current_route_number = next_line if next_line else None

            else:
                parts = line.split(",")
                if len(parts) < 3 or len(parts) > 4:
                    print(
                        f"Warning: Invalid line format (strange number of parts): {line}"
                    )
                    continue

                trip_id = parts[0].strip()
                point_id = parts[1].strip()
                full_names = parts[2]
                full_names = full_names.strip().split("^")

                short_names = None
                if len(parts) == 4:
                    short_names = parts[3]
                    short_names = short_names.strip().split("^")

                current_trips.append(
                    {
                        "trip_id": trip_id,
                        "point_id": point_id,
                        "full_name": full_names,
                        "short_name": short_names,
                    }
                )

        self._db_manager.with_db(
            lambda db: flush_route(db, current_route_number, current_trips)
        )
        lines = None
        self._db_manager.close()
        gc.collect()
        self._db_manager.reopen()

    def _build_index(self):
        def inner(db):
            t = db.table("routes")
            docs = t.all()
            self._route_doc_ids = [d.doc_id for d in docs]
            self._route_count = len(self._route_doc_ids)

        self._db_manager.with_db(inner)

    def get_route_by_index(self, route_idx: int):
        doc_id = self._route_doc_ids[route_idx]
        return self._db_manager.with_db(
            lambda db: db.table("routes").get(doc_id=doc_id)
        )

    def get_length_of_routes(self) -> int:
        return self._route_count

    def get_length_of_trips(self, route_idx: int) -> int:
        route = self.get_route_by_index(route_idx)
        return len(route.get("dirs", [])) if route else 0
