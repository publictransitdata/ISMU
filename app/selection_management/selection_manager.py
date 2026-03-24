import os

import ujson as json

from app.config_management.config_info import SystemConfig
from app.error_codes import ErrorCodes
from app.routes_management.routes_manager import RoutesManager
from utils.error_handler import set_error_and_raise
from utils.singleton_decorator import singleton

SELECTION_PATH = "app/selection_management/selection.json"
TEMP_SELECTION_PATH = "app/selection_management/selection.tmp"


class TripInfo:
    def __init__(
        self,
        group_id: str,
        point_id: str,
        full_name: list[str],
        short_name: list[str] | None,
    ):
        self.group_id = group_id
        self.point_id = point_id
        self.full_name = full_name
        self.short_name = short_name

    @staticmethod
    def trip_from_dict(d: dict | None):
        if d is not None:
            group_id = d.get("trip_id", "")
            point_id = d.get("point_id", "")
            full_name = d.get("full_name") or []
            short_name = d.get("short_name") or []
            return TripInfo(group_id, point_id, full_name, short_name)
        else:
            return None

    def get_proper_trip_name(self) -> list[str]:
        if SystemConfig().force_short_names:
            if self.short_name:
                return self.short_name
            else:
                return self.full_name
        else:
            return self.full_name


class ActiveSelection:
    def __init__(self):
        self.route_number: str | None = None
        self.trip: TripInfo | None = None
        self.no_line_telegram: bool = False
        self.is_updated: bool = False

    def apply(self, route_number: str | None, trip: dict | None, no_line_telegram: bool = False):
        self.route_number = route_number
        self.trip = TripInfo.trip_from_dict(trip)
        self.no_line_telegram = no_line_telegram
        self.is_updated = True

    def reset(self):
        self.route_number = None
        self.trip = None
        self.no_line_telegram = False
        self.is_updated = False


@singleton
class SelectionManager:
    def __init__(self):
        self._active_selection = ActiveSelection()

    def get_selection_ids(self):
        selection_info = self._load_from_file()
        if selection_info is None:
            return {"route_id": 0, "trip_id": 0}
        return selection_info

    def get_active_selection(self) -> ActiveSelection:
        if self._active_selection.route_number is None:
            ids = self.get_selection_ids()
            self._enrich_from_routes(ids["route_id"], ids["trip_id"])
        return self._active_selection

    def update_selection(self, route_id: int, trip_id: int):
        self._save_to_file(route_id, trip_id)
        self._enrich_from_routes(route_id, trip_id)

    def reset_selection(self):
        self._save_to_file(0, 0)
        self._active_selection.reset()

    def _load_from_file(self) -> dict | None:
        try:
            with open(SELECTION_PATH) as file:
                return json.loads(file.read())
        except OSError:
            pass

        try:
            with open(TEMP_SELECTION_PATH) as file:
                return json.loads(file.read())
        except OSError:
            return None

    def _save_to_file(self, selected_route_id, selected_trip_id):
        try:
            rec = {
                "route_id": selected_route_id,
                "trip_id": selected_trip_id,
            }
            with open(TEMP_SELECTION_PATH, "w") as file:
                file.write(json.dumps(rec))
                file.flush()

            os.sync()
            os.rename(TEMP_SELECTION_PATH, SELECTION_PATH)
            os.sync()

        except OSError as err:
            set_error_and_raise(ErrorCodes.TEMP_SELECTION_WRITE_ERROR, err, show_message=True)

    def _enrich_from_routes(self, route_id: int, trip_id: int) -> None:
        route = RoutesManager().get_route_by_index(route_id)
        if route and route.get("dirs"):
            dirs = route["dirs"]
            trip = dirs[trip_id] if trip_id < len(dirs) else None
            self._active_selection.apply(
                route_number=route["route_number"],
                trip=trip,
                no_line_telegram=route.get("no_line_telegram", False),
            )
        else:
            self._active_selection.reset()
