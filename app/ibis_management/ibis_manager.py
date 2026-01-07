from utils.singleton_decorator import singleton
from app.config_loading import ConfigManager
import uasyncio as asyncio
import ujson as json

try:
    with open("/config/char_map.json") as f:
        char_map = json.load(f)
except Exception as e:
    print(f"Error loading char_map.json: {e}")
    char_map = {}


TELEGRAM_FORMATS = {
    "DS001": "l{:0>3}",
    "DS001neu": "q{:0>4}",
    "DS003": "z{:03d}",
    "DS003a": "zA2{: <32}",
    # "DS003b":  "zR{:03d}", no description in documentation
    "DS003c": None,  # no description in documentation
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

        self.dispatch = {
            "DS001": self.DS001,
            "DS001neu": self.DS001neu,
            "DS003": self.DS003,
            "DS003a": self.DS003a,
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
        try:
            if value is None:
                raise ValueError("Route number is None")
            formatted = format.format(int(value))
        except Exception as e:
            print(f"Error formatting DS001 with value '{value}': {e}")
            formatted = format.format(0)

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS001neu(self):
        value = self.config_manager.get_current_configuration().route_number
        format = TELEGRAM_FORMATS["DS001neu"]
        if isinstance(value, str):
            value = self.sanitize_ibis_text(value)
        try:
            formatted = format.format(value)
        except Exception as e:
            print(f"Error formatting DS001neu with value '{value}': {e}")
            formatted = format.format("0000")

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS003(self):
        value = self.config_manager.get_current_configuration().route_number
        format = TELEGRAM_FORMATS["DS003"]
        try:
            if value is None:
                raise ValueError("Route number is None")
            formatted = format.format(int(value))
        except Exception as e:
            print(f"Error formatting DS003 with value '{value}': {e}")
            formatted = format.format(0)

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    def DS003a(self):
        trip = self.config_manager.get_current_configuration().trip
        if trip is None:
            print("Error: Trip information is None for DS003a telegram.")
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
            print(f"Error formatting DS003a with value '{value}': {e}")
            formatted = "zA2" + ("?" * 32)

        packet = self.create_ibis_packet(formatted)
        self.uart.write(packet)

    async def send_ibis_telegrams(self):
        self._running = True
        while self._running:
            if (
                self.config_manager.get_current_configuration().route_number is not None
                and self.config_manager.get_current_configuration().trip is not None
            ):
                for code in self.telegramTypes:
                    handler = self.dispatch.get(code)
                    if handler:
                        try:
                            handler()
                            await asyncio.sleep_ms(5)
                        except Exception as e:
                            print("Error", code, ":", e)
                    else:
                        print("Unknown telegram:", code)
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
