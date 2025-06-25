from .singleton_decorator import singleton


class SystemConfig:
    def __init__(self):
        self._line: str = ""
        self._dest_num: str = ""
        self._destination: str = ""
        self._display_start_and_dist: bool = False
        self._forse_short_names: bool = False
        self._stop_display: str = ""
        self._rt_on_stop_disp: bool = False
        self._ap_name: str = ""
        self._ap_pswd: str = ""
        self._ap_ip: str = ""
        self._version: str = "0.1.0"

    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, value):
        self._line = value

    @property
    def dest_num(self):
        return self._dest_num

    @dest_num.setter
    def dest_num(self, value):
        self._dest_num = value

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, value):
        self._destination = value

    @property
    def display_start_and_dist(self):
        return self._display_start_and_dist

    @display_start_and_dist.setter
    def display_start_and_dist(self, value):
        self._display_start_and_dist = value

    @property
    def forse_short_names(self):
        return self._forse_short_names

    @forse_short_names.setter
    def forse_short_names(self, value):
        self._forse_short_names = value

    @property
    def stop_display(self):
        return self._stop_display

    @stop_display.setter
    def stop_display(self, value):
        self._stop_display = value

    @property
    def rt_on_stop_disp(self):
        return self._rt_on_stop_disp

    @rt_on_stop_disp.setter
    def rt_on_stop_disp(self, value):
        self._rt_on_stop_disp = value

    @property
    def ap_name(self):
        return self._ap_name

    @ap_name.setter
    def ap_name(self, value):
        self._ap_name = value

    @property
    def ap_pswd(self):
        return self._ap_pswd

    @ap_pswd.setter
    def ap_pswd(self, value):
        self._ap_pswd = value

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
