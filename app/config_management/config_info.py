from utils.singleton_decorator import singleton

AP_NAME = "ismu-hotspot"
AP_PASSWORD = "12345678"
AP_IP = "192.168.4.1"
VERSION = "1.0.0"


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
        self.version: str = VERSION
