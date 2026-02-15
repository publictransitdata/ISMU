from app.error_codes import ErrorCodes
from utils.singleton_decorator import singleton
from utils.error_handler import set_error_and_raise
from utils.message_handler import set_message
from app.config_management import SystemConfig
from app.config_management import ConfigManager
import uasyncio as asyncio
import ujson as json

try:
    with open("/config/char_map.json") as f:
        char_map = json.load(f)
except Exception as e:
    set_error_and_raise(ErrorCodes.CHAR_MAP_LOAD_ERROR)
    char_map = {}


TELEGRAM_FORMATS = {
    "DS001": "l{:0>3}",
    "DS001neu": "q{:0>4}",
    "DS003": "z{:03d}",
    "DS003a": "zA2{: <32}",
    "DS003b": "zR{:03d}",  # no description in documentation
    "DS003c": "zI6{: <24}",
    "DS003d": "zN{:03d}",
    "DS3aMAS": None,  # no description in documentation
    "DS009": "v{: <16}",
    "DS3cneu": None,  # no description in documentation
}


@singleton
class IBISManager:
    def __init__(self, uart, telegramTypes):
        self.uart = uart
        self._running = False
        self._task = None
        self.telegramTypes = telegramTypes
        self.config_manager = ConfigManager()
        self._system_config = SystemConfig()
        self._failed_telegrams = set()

        self.dispatch = {
            "DS001": self.DS001,
            "DS001neu": self.DS001neu,
            "DS003": self.DS003,
            "DS003a": self.DS003a,
            "DS003c": self.DS003c,
        }

    def calculate_ibis_checksum(self, data_bytes):
        parity = 0x7F
        for byte in data_bytes:
            parity ^= byte
        return parity

    def create_ibis_packet(self, formatted_string):
        message_bytes = formatted_string.encode("ascii") + b"\x0d"

        parity_byte = self.calculate_ibis_checksum(message_bytes)

        packet = message_bytes + bytes([parity_byte])

        # Log the telegram packet details
        print("Sending IBIS telegram:")
        print(f"  ASCII: {formatted_string}")
        print(f"  HEX: {packet.hex().upper()}")

        return packet

    def sanitize_ibis_text(self, text):
        """
        If it’s a standard printable ASCII character (code point 32–126), it’s kept unchanged.
        If it’s not ASCII but exists in the char_map, it gets replaced with the mapped value.
        If it’s neither ASCII nor in the map, it gets replaced with a ?.
        """
        sanitized = ""
        for c in text:
            if 32 <= ord(c) <= 126:
                sanitized += c
            elif c in char_map:
                sanitized += char_map[c]
            else:
                sanitized += "?"
        return sanitized

    def DS001(self):
        value = self.config_manager.get_current_configuration().route_number
        format = TELEGRAM_FORMATS["DS001"]
        if value is None:
            set_error_and_raise(ErrorCodes.ROUTE_NUMBER_IS_NONE)
        try:
            formatted = format.format(int(value))
        except Exception as e:
            set_message("Номер маршруту не виводиться")
            self._failed_telegrams.add("DS001")
            formatted = format.format(0)

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS001neu(self):
        value = self.config_manager.get_current_configuration().route_number
        format = TELEGRAM_FORMATS["DS001neu"]
        if isinstance(value, str):
            value = self.sanitize_ibis_text(value)
        if value is None:
            set_error_and_raise(ErrorCodes.ROUTE_NUMBER_IS_NONE)
        try:
            formatted = format.format(value)
        except Exception as e:
            set_message("Номер маршруту не виводиться")
            self._failed_telegrams.add("DS001neu")
            formatted = format.format("0000")

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS003(self):
        trip = self.config_manager.get_current_configuration().trip
        if trip is None:
            set_error_and_raise(ErrorCodes.TRIP_INFO_IS_NONE)
            return

        value = trip.point_id
        format = TELEGRAM_FORMATS["DS003"]
        if value is None:
            set_error_and_raise(ErrorCodes.POINT_ID_IS_NONE)
        try:
            formatted = format.format(int(value))
        except Exception as e:
            set_message("Код напрямку не відправляється")
            self._failed_telegrams.add("DS003")
            formatted = format.format(0000)

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS003a(self):
        trip = self.config_manager.get_current_configuration().trip
        if trip is None:
            set_error_and_raise(ErrorCodes.TRIP_INFO_IS_NONE)
            return

        value = trip.full_name
        if len(value) == 2:
            value = value[1]
        else:
            value = value[0]

        format = TELEGRAM_FORMATS["DS003a"]
        if isinstance(value, str):
            value = self.sanitize_ibis_text(value)
        try:
            formatted = format.format(value[:32])
        except Exception as e:
            set_message("Текст на зовнішньому табло не відображається")
            self._failed_telegrams.add("DS003a")
            formatted = "zA2" + (" " * 32)

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS003c(self):
        if self._system_config.show_info_on_stop_board:
            route_number = self.config_manager.get_current_configuration().route_number
            trip = self.config_manager.get_current_configuration().trip

            if trip is None:
                set_error_and_raise(ErrorCodes.TRIP_INFO_IS_NONE)
                return
            format = TELEGRAM_FORMATS["DS003c"]

            if isinstance(route_number, str):
                route_number = self.sanitize_ibis_text(route_number)
            if route_number is None:
                set_error_and_raise(ErrorCodes.ROUTE_NUMBER_IS_NONE)

            trip_name = trip.full_name

            if len(trip_name) == 2:
                trip_name = trip_name[1]
            else:
                trip_name = trip_name[0]

            if isinstance(trip_name, str):
                trip_name = self.sanitize_ibis_text(trip_name)
            try:
                formatted = format.format((route_number + " > " + trip_name)[:24])
            except Exception as e:
                set_message("Текст на внутрішньому табло не відображається")
                self._failed_telegrams.add("DS003c")
                formatted = "zI6" + (" " * 24)

            packet = self.create_ibis_packet(formatted)
            self.uart.write(packet)
        else:
            pass

    async def send_ibis_telegrams(self):
        self._running = True
        while self._running:
            current_config = self.config_manager.get_current_configuration()
            if current_config.isUpdated:
                self._failed_telegrams.clear()
                current_config.isUpdated = False
            if (
                current_config.route_number is not None
                and current_config.trip is not None
            ):
                for code in self.telegramTypes:
                    if code in self._failed_telegrams:
                        continue
                    if (
                        code in ("DS001", "DS001neu")
                        and current_config.no_line_telegram
                    ):
                        continue

                    handler = self.dispatch.get(code)
                    if handler:
                        handler()
                        await asyncio.sleep_ms(5)
                    else:
                        set_error_and_raise(ErrorCodes.UNKNOWN_TELEGRAM)
            await asyncio.sleep(10)

    @property
    def task(self):
        return self._task

    def start(self):
        """Start async loop as a task"""
        if not self._task:
            self._task = asyncio.create_task(self.send_ibis_telegrams())

    def stop(self):
        """Stop async loop"""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
