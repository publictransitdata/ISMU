from app.routes_management import RoutesManager
from app.selection_management import SelectionManager
from utils.singleton_decorator import singleton

AP_NAME = "ismu-hotspot"
AP_PASSWORD = "12345678"
AP_IP = "192.168.4.1"


@singleton
class SystemConfig:
    def __init__(self):
        self.line_telegram: str = ""
        self.destination_number_telegram: str = ""
        self.destination_telegram: str = ""
        self.show_start_and_end_stops: bool = False
        self.force_short_names: bool = False
        self.stop_board_telegram: str = ""
        self.show_info_on_stop_board: bool = False
        self.ap_name: str = AP_NAME
        self.ap_password: str = AP_PASSWORD
        self.ap_ip: str = AP_IP
        self.baudrate: int = 1200
        self.bits: int = 7
        self.parity: int = 2
        self.stop: int = 2
        self.version: str = "1.0.0"


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


class CurrentRouteTripSelection:
    def __init__(
        self,
        route_number: str | None = None,
        trip: dict | None = None,
        no_line_telegram: bool = False,
    ):
        self.route_number = route_number
        self.trip = TripInfo.trip_from_dict(trip)
        self.no_line_telegram = no_line_telegram
        self.is_updated = False

    def load_from_saved_selection(self):
        selection = SelectionManager().get_selection()
        route = RoutesManager().get_route_by_index(selection["route_id"])

        if route and route.get("dirs"):
            self.route_number = route["route_number"]
            dirs = route["dirs"]
            trip_id = selection.get("trip_id", 0)
            if trip_id < len(dirs):
                self.trip = TripInfo.trip_from_dict(dirs[trip_id])
            self.no_line_telegram = route.get("no_line_telegram", False)
