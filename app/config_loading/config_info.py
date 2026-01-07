from utils.singleton_decorator import singleton


@singleton
class SystemConfig:
    def __init__(self):
        self._line: str = ""
        self._destination_number: str = ""
        self._destination: str = ""
        self._display_start_and_end_stops: bool = False
        self._force_short_names: bool = False
        self._stop_display_telegram: str = ""
        self._display_route_on_stop_board: bool = False
        self._ap_name: str = ""
        self._ap_password: str = ""
        self._ap_ip: str = ""

        ## is that variable need to be here?
        self._version: str = "0.1.0"

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
    def display_start_and_end_stops(self):
        return self._display_start_and_end_stops

    @display_start_and_end_stops.setter
    def display_start_and_end_stops(self, value):
        self._display_start_and_end_stops = value

    @property
    def force_short_names(self):
        return self._force_short_names

    @force_short_names.setter
    def force_short_names(self, value):
        self._force_short_names = value

    @property
    def stop_display_telegram(self):
        return self._stop_display_telegram

    @stop_display_telegram.setter
    def stop_display_telegram(self, value):
        self._stop_display_telegram = value

    @property
    def display_route_on_stop_board(self):
        return self._display_route_on_stop_board

    @display_route_on_stop_board.setter
    def display_route_on_stop_board(self, value):
        self._display_route_on_stop_board = value

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


class CurrentSystemChosenConfiguraion:
    def __init__(self, route_number: str | None = None, trip: dict | None = None):
        self.route_number = route_number
        self.trip = TripInfo.trip_from_dict(trip)
