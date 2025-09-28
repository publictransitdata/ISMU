from machine import Pin, I2C, UART

import time



 # Шаблони телеграм
TELEGRAM_FORMATS = {
    "DS001":   "l{:0>3}",
    "DS003c":  "z{: <16}",
    "DS003b":  "zR{:03d}",
    # додай інші типи за потреби
}

class IBISManager:
    def __init__(
        self,
        uart,
        char_map
    ):
        self.uart = uart
        self.char_map = char_map


    # QWERTY -> ЙЦУКЕН символи для української
    def sanitize_ibis_text(self, text):
        sanitized = ''
        for c in text:
            if 32 <= ord(c) <= 126:
                sanitized += c
            elif c in self.char_map:
                sanitized += self.char_map[c]
            else:
                sanitized += '?'
        return sanitized

   

    def encode_ibis_telegram(self, code, value):
        if code not in TELEGRAM_FORMATS:
            raise ValueError(f"Unsupported telegram type: {code}")

        format = TELEGRAM_FORMATS[code]
        if isinstance(value, str):
            print(value)
            value = self.sanitize_ibis_text(value)
            print(value)

        try:
            if format.endswith('d}'):
                formatted = format.format(int(value))
            else:
                formatted = format.format(value)
        except Exception as e:
            print(f"Error formatting {code} with value '{value}': {e}")
            formatted = format.format('?')

        packet = formatted.encode('ascii') + b'\r/'
        print(f"Sending IBIS Packet: ASCII: {formatted}, HEX: {packet.hex().upper()}")
        return packet

    def send_ibis_telegrams(self, telegrams):
        for code, value in telegrams.items():
            tg = self.encode_ibis_telegram(code, value)
            self.uart.write(tg)
            time.sleep(0.05)
