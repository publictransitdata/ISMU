import uasyncio as asyncio
import ujson as json

from app.config_management import SystemConfig
from app.error_codes import ErrorCodes
from app.selection_management import SelectionManager
from utils.custom_error import CustomError
from utils.error_handler import set_error_and_raise
from utils.gui_hooks import trigger_message
from utils.i18n import string
from utils.singleton_decorator import singleton

TELEGRAM_FORMATS = {
    "DS001": "l{:0>3}",
    "DS001neu": "q{:0>4}",
    "lE": "lE{:02d}",
    "qE": "qE{:02d}",
    "DS003": "z{:03d}",
    "DS003a": "zA2{: <32}",
    "DS003b": "zR{:03d}",  # no description in documentation
    "DS003c": "zI6{: <24}",
    "DS003d": "zN{:03d}",
    "DS3aMAS": None,  # no description in documentation
    "DS009": "v{: <16}",
    "DS3cneu": None,  # no description in documentation
}

TEXT_BLOCK_SIZE = 16
RESEND_INTERVAL_MS = 10000
CHANGE_POLL_MS = 100


def ibis_hex(value: int) -> str:
    return "".join(chr(0x30 + int(digit, 16)) for digit in f"{value:X}")


def blocks_for(length: int) -> int:
    return (length + TEXT_BLOCK_SIZE - 1) // TEXT_BLOCK_SIZE


def layout_rows(rows: list, mode: str, width: int) -> str:
    if mode == "flowing":
        return "".join(rows)
    if mode == "line_feed":
        rows = list(rows)
        while rows and not rows[-1]:
            rows.pop()
        return "\n".join(rows) + "\n\n"
    return "".join((row + " " * width)[:width] for row in rows)


def ds021_payload(addr: int, text: str) -> str:
    blocks = blocks_for(len(text))
    padding = " " * (blocks * TEXT_BLOCK_SIZE - len(text))
    return "aA" + ibis_hex(addr) + ibis_hex(blocks) + text + padding


def ds021t_payload(addr: int, rows: list, cycle: int) -> str:
    upper = rows[0] if rows else ""
    lower = rows[1] if len(rows) > 1 else ""
    return ds021_payload(addr, "A" + ibis_hex(cycle) + upper + "\n" + lower + "\n\n")


def ds021neu_payload(addr: int, rows: list, font: str) -> str:
    line1 = rows[0] if rows else ""
    line2 = rows[1] if len(rows) > 1 else ""
    text = ((line1 or " ") + "\n" + line2 if line2 else line1) + "\n\n"
    suffix = "\n.CM" + font
    blocks = blocks_for(len(text) + len(suffix))
    padding = " " * (blocks * TEXT_BLOCK_SIZE - len(text) - len(suffix))
    return "aA" + ibis_hex(addr) + ibis_hex(blocks) + text + padding + suffix


@singleton
class IBISManager:
    def __init__(self, uart, telegramTypes):
        self.uart = uart
        self._running = False
        self.task = None
        self.telegramTypes = telegramTypes
        self.selection_manager = SelectionManager()
        self._system_config = SystemConfig()
        self._failed_telegrams = set()
        self._char_map = {}

        self.dispatch = {
            "DS001": self.DS001,
            "DS001neu": self.DS001neu,
            "DS003": self.DS003,
            "DS003a": self.DS003a,
            "DS003c": self.DS003c,
            "DS021": self.DS021,
            "DS021neu": self.DS021neu,
            "DS021T": self.DS021T,
        }

        if self._system_config.use_char_map:
            try:
                with open("/config/char_map.json") as f:
                    self._char_map = json.load(f)
            except Exception:
                set_error_and_raise(ErrorCodes.CHAR_MAP_LOAD_ERROR)
        else:
            self._char_map = {}

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
            elif c in self._char_map:
                sanitized += self._char_map[c]
            else:
                sanitized += "?"
        return sanitized

    def DS001(self):
        selection = self.selection_manager.get_active_selection()
        if selection.no_line_telegram:
            self._send_nlt_data("l", width=3)
            return
        if selection.special_char is not None:
            self._send_special_char("lE", selection.special_char)
            return

        value = selection.route_number
        format = TELEGRAM_FORMATS["DS001"]
        if value is None:
            raise CustomError(ErrorCodes.ROUTE_NUMBER_IS_NONE, string("ibis_msg_no_route"))
        try:
            formatted = format.format(int(value))
        except Exception as err:
            raise CustomError(ErrorCodes.ROUTE_VALUE_IS_WRONG, string("ibis_msg_no_route")) from err

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS001neu(self):
        selection = self.selection_manager.get_active_selection()
        if selection.no_line_telegram:
            self._send_nlt_data("q", width=4)
            return
        if selection.special_char is not None:
            self._send_special_char("qE", selection.special_char)
            return

        value = selection.route_number
        format = TELEGRAM_FORMATS["DS001neu"]
        if isinstance(value, str):
            value = self.sanitize_ibis_text(value)
        if value is None:
            raise CustomError(ErrorCodes.ROUTE_NUMBER_IS_NONE, string("ibis_msg_no_route"))
        try:
            formatted = format.format(value)
        except Exception as err:
            raise CustomError(ErrorCodes.ROUTE_VALUE_IS_WRONG, string("ibis_msg_no_route")) from err

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def _send_nlt_data(self, prefix: str, width: int):
        data = self._system_config.nlt_data
        if data is None:
            data = "0" * width

        packet = self.create_ibis_packet(prefix + data)
        self.uart.write(packet)

    def _send_special_char(self, format_key: str, value: int):
        try:
            formatted = TELEGRAM_FORMATS[format_key].format(value)
        except Exception as err:
            raise CustomError(ErrorCodes.ROUTE_VALUE_IS_WRONG, string("ibis_msg_no_route")) from err

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS003(self):
        trip = self.selection_manager.get_active_selection().trip
        if trip is None:
            raise CustomError(ErrorCodes.TRIP_INFO_IS_NONE, string("ibis_msg_no_trip_code"))

        value = trip.point_id
        format = TELEGRAM_FORMATS["DS003"]
        if value is None:
            raise CustomError(ErrorCodes.POINT_ID_IS_NONE, string("ibis_msg_no_trip_code"))
        try:
            formatted = format.format(value)
        except Exception as err:
            raise CustomError(ErrorCodes.POINT_ID_VALUE_IS_WRONG, string("ibis_msg_no_trip_code")) from err

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS003a(self):
        trip = self.selection_manager.get_active_selection().trip
        if trip is None:
            raise CustomError(
                ErrorCodes.TRIP_INFO_IS_NONE,
                string("ibis_msg_no_outer_text"),
            )
        names = trip.get_proper_trip_name()
        if len(names) == 2 and self._system_config.show_start_and_end_stops:
            start_stop = f"{self.sanitize_ibis_text(names[0][:16]): <16}"
            end_stop = f"{self.sanitize_ibis_text(names[1][:16]): <16}"
            value = start_stop + end_stop
        elif len(names) == 2:
            value = self.sanitize_ibis_text(names[1])
        else:
            value = self.sanitize_ibis_text(names[0])
        format = TELEGRAM_FORMATS["DS003a"]
        try:
            formatted = format.format(value[:32])
        except Exception as err:
            raise CustomError(
                ErrorCodes.TRIP_NAME_IS_WRONG,
                string("ibis_msg_no_outer_text"),
            ) from err
        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS003c(self):
        if self._system_config.show_info_on_stop_board:
            route_number = self.selection_manager.get_active_selection().route_number
            trip = self.selection_manager.get_active_selection().trip

            if trip is None:
                raise CustomError(
                    ErrorCodes.TRIP_INFO_IS_NONE,
                    string("ibis_msg_no_inner_text"),
                )
            format = TELEGRAM_FORMATS["DS003c"]

            if route_number is None:
                raise CustomError(
                    ErrorCodes.ROUTE_NUMBER_IS_NONE,
                    string("ibis_msg_no_inner_text"),
                )
            if isinstance(route_number, str):
                route_number = self.sanitize_ibis_text(route_number)

            trip_name = trip.get_proper_trip_name()

            if len(trip_name) == 2:
                trip_name = trip_name[1]
            else:
                trip_name = trip_name[0]

            if trip_name is None:
                raise CustomError(
                    ErrorCodes.TRIP_NAME_IS_NONE,
                    string("ibis_msg_no_inner_text"),
                )
            if isinstance(trip_name, str):
                trip_name = self.sanitize_ibis_text(trip_name)
            try:
                formatted = format.format((route_number + " > " + trip_name)[:24])
            except Exception as err:
                raise CustomError(
                    ErrorCodes.TRIP_NAME_OR_ROUTE_NUMBER_IS_WRONG,
                    string("ibis_msg_no_inner_text"),
                ) from err

            packet = self.create_ibis_packet(formatted)
            self.uart.write(packet)
        else:
            pass

    def DS021(self):
        for display in self._enabled_displays():
            text = layout_rows(self._display_rows(display), display.get("mode", "fixed"), display.get("width", 16))
            packet = self.create_ibis_packet(ds021_payload(display["addr"], text))
            self.uart.write(packet)

    def DS021T(self):
        for display in self._enabled_displays():
            payload = ds021t_payload(display["addr"], self._display_rows(display), display.get("cycle", 0))
            packet = self.create_ibis_packet(payload)
            self.uart.write(packet)

    def DS021neu(self):
        for display in self._enabled_displays():
            payload = ds021neu_payload(display["addr"], self._display_rows(display), display.get("font", ""))
            packet = self.create_ibis_packet(payload)
            self.uart.write(packet)

    def _enabled_displays(self) -> list:
        return [display for display in self._system_config.displays if display.get("enabled", True)]

    def _display_rows(self, display) -> list:
        selection = self.selection_manager.get_active_selection()
        if selection.trip is None:
            raise CustomError(ErrorCodes.TRIP_INFO_IS_NONE, string("ibis_msg_no_outer_text"))

        names = [self.sanitize_ibis_text(name) for name in selection.trip.get_proper_trip_name()]
        destination = names[-1] if names else ""

        if display.get("display_type", "external") == "internal":
            return [self.sanitize_ibis_text(selection.route_number or "") + " > " + destination]

        show_start_and_end_stops = display.get(
            "show_start_and_end_stops",
            self._system_config.show_start_and_end_stops,
        )
        if len(names) == 2 and show_start_and_end_stops:
            return names
        return [destination]

    async def send_ibis_telegrams(self):
        self._running = True
        while self._running:
            active_selection = self.selection_manager.get_active_selection()
            if active_selection.is_updated:
                self._failed_telegrams.clear()
                active_selection.is_updated = False
            if active_selection.route_number is not None and active_selection.trip is not None:
                for code in self.telegramTypes:
                    if code in self._failed_telegrams:
                        continue

                    handler = self.dispatch.get(code)
                    if handler:
                        try:
                            handler()
                        except CustomError as err:
                            self._failed_telegrams.add(code)
                            trigger_message(err.detail, err.error_code)
                        await asyncio.sleep_ms(5)
                    else:
                        self._running = False
                        set_error_and_raise(
                            ErrorCodes.UNKNOWN_TELEGRAM,
                            RuntimeError(string("ibis_err_unknown_telegram").format(code)),
                            show_message=True,
                            raise_exception=False,
                        )
                        break
            await self._wait_for_selection_change(active_selection)

    async def _wait_for_selection_change(self, selection):
        waited = 0
        while self._running and not selection.is_updated and waited < RESEND_INTERVAL_MS:
            await asyncio.sleep_ms(CHANGE_POLL_MS)
            waited += CHANGE_POLL_MS

    def start(self):
        """Start async loop as a task"""
        if not self.task:
            self.task = asyncio.create_task(self.send_ibis_telegrams())

    def stop(self):
        """Stop async loop"""
        self._running = False
        if self.task:
            self.task.cancel()
            self.task = None
