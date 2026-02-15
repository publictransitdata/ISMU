from utils.singleton_decorator import singleton
from app.state_management import StateManager
from app.routes_management import RoutesManager

AP_NAME = "ismu-hotspot"
AP_PASSWORD = "12345678"
AP_IP = "192.168.4.1"


@singleton
class SystemConfig:
    def __init__(self):
        self._line: str = ""
        self._destination_number: str = ""
        self._destination: str = ""
        self._show_start_and_end_stops: bool = False
        self._force_short_names: bool = False
        self._stop_board_telegram: str = ""
        self._show_info_on_stop_board: bool = False
        self._ap_name: str = AP_NAME
        self._ap_password: str = AP_PASSWORD
        self._ap_ip: str = AP_IP
        self._baudrate: int = 1200
        self._bits: int = 7
        self._parity: int = 2
        self._stop: int = 2

        ## is that variable need to be here?
        self._version: str = "1.0.0"

    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, value):
        self._line = value

    @property
    def destination_number(self):
        return self._destination_number

    @destination_number.setter
    def destination_number(self, value):
        self._destination_number = value

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, value):
        self._destination = value

    @property
    def show_start_and_end_stops(self):
        return self._show_start_and_end_stops

    @show_start_and_end_stops.setter
    def show_start_and_end_stops(self, value):
        self._show_start_and_end_stops = value

    @property
    def force_short_names(self):
        return self._force_short_names

    @force_short_names.setter
    def force_short_names(self, value):
        self._force_short_names = value

    @property
    def stop_board_telegram(self):
        return self._stop_board_telegram

    @stop_board_telegram.setter
    def stop_board_telegram(self, value):
        self._stop_board_telegram = value

    @property
    def show_info_on_stop_board(self):
        return self._show_info_on_stop_board

    @show_info_on_stop_board.setter
    def show_info_on_stop_board(self, value):
        self._show_info_on_stop_board = value

    @property
    def ap_name(self):
        return self._ap_name

    @ap_name.setter
    def ap_name(self, value):
        self._ap_name = value

    @property
    def ap_password(self):
        return self._ap_password

    @ap_password.setter
    def ap_password(self, value):
        self._ap_password = value

    @property
    def ap_ip(self):
        return self._ap_ip

    @ap_ip.setter
    def ap_ip(self, value):
        self._ap_ip = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, value):
        self._baudrate = value

    @property
    def bits(self):
        return self._bits

    @bits.setter
    def bits(self, value):
        self._bits = value

    @property
    def parity(self):
        return self._parity

    @parity.setter
    def parity(self, value):
        self._parity = value

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, value):
        self._stop = value


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

    def get_proper_trip_name(self) -> list[str] | None:
        if SystemConfig().force_short_names:
            if self.short_name:
                return self.short_name
            else:
                return self.full_name
        else:
            return self.full_name


class CurrentSystemChosenConfiguraion:
    def __init__(
        self,
        route_number: str | None = None,
        trip: dict | None = None,
        no_line_telegram: bool = False,
    ):
        self.route_number = route_number
        self.trip = TripInfo.trip_from_dict(trip)
        self.no_line_telegram = no_line_telegram
        self.isUpdated = False

    def load_from_saved_state(self):
        state = StateManager().get_state()
        route = RoutesManager().get_route_by_index(state["route_id"])

        if route and route.get("dirs"):
            self._route_number = route["route_number"]
            dirs = route["dirs"]
            trip_id = state.get("trip_id", 0)
            if trip_id < len(dirs):
                self._trip = TripInfo.trip_from_dict(dirs[trip_id])
            self._no_line_telegram = route.get("no_line_telegram", False)

    @property
    def route_number(self):
        return self._route_number

    @route_number.setter
    def route_number(self, value):
        self._route_number = value

    @property
    def trip(self):
        return self._trip

    @trip.setter
    def trip(self, value):
        self._trip = value

    @property
    def no_line_telegram(self):
        return self._no_line_telegram

    @no_line_telegram.setter
    def no_line_telegram(self, value):
        self._no_line_telegram = value
