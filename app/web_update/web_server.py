from app.web_update.safe_route_decorator import safe_route
from microdot import Microdot  # type: ignore
import network
import uasyncio as asyncio
import os
import machine

ALLOWED_CHARS = set(
    " !\"'+,-./0123456789:<=>?ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_abcdefghijklmnopqrstuvwxyz()ÓóĄąĆćĘęŁłŚśŻżЄІЇАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзийклмнопрстуфхцчшщьюяєії^#|\n\r,+"
)

ALLOWED_CONFIG_CHARS = set(
    " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_=.-\n\r"
)


VALID_CONFIG_KEYS = {
    "show_start_and_end_stops",
    "force_short_names",
    "show_route_on_stop_board",
    "baudrate",
    "bits",
    "parity",
    "stop",
    "line",
    "destination_number",
    "destination",
    "stop_board_telegram",
    "ap_name",
    "ap_password",
    "ap_ip",
}


BASE_STYLE = """body{font-family:Arial;margin:0;padding:0;background:#f5f5f5;display:flex;align-items:center;justify-content:center;min-height:100vh}.c{background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1);max-width:400px;width:90%;text-align:center}h1{font-size:1.5em;margin-bottom:1em}"""

UPLOAD_HTML = (
    """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Завантажити</title><style>"""
    + BASE_STYLE
    + """p{margin:.5em 0 .2em;text-align:left}input[type=file]{width:100%}input[type=submit]{margin-top:1em;width:100%;padding:.7em;font-size:1em;background:#4CAF50;color:#fff;border:none;border-radius:4px;cursor:pointer}</style></head><body><div class="c"><h1>Режим оновлення</h1><form action="/upload" method="post" enctype="multipart/form-data"><p>Завантажити config.txt:</p><input type="file" name="config_file"><p>Завантажити routes.txt:</p><input type="file" name="routes_file"><input type="submit" value="Завантажити"></form></div></body></html>"""
)

SUCCESS_HTML = (
    """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Успіх</title><style>"""
    + BASE_STYLE
    + """.ok{color:#4CAF50;font-size:3em}p{margin:1em 0}</style></head><body><div class="c"><div class="ok">&#10004;</div><h1>Успішно завантажено</h1><p>Збережені файли: {files}</p><p>Пристрій перезавантажиться...</p></div></body></html>"""
)

ERROR_HTML = (
    """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Помилка</title><style>"""
    + BASE_STYLE
    + """.err{color:#f44336;font-size:3em}p{margin:1em 0}a{display:inline-block;margin-top:1em;padding:.5em 1em;background:#4CAF50;color:#fff;text-decoration:none;border-radius:4px}</style></head><body><div class="c"><div class="err">&#10008;</div><h1>Помилка</h1><p>{message}</p><a href="/">Спробувати ще раз</a></div></body></html>"""
)


def _check_invalid_chars(content: bytes, allowed_chars: set) -> list:
    errors = []
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as e:
        return [f"Невірне кодування файлу (позиція {e.start})"]

    for i, char in enumerate(text):
        if char not in allowed_chars:
            line_num = text[:i].count("\n") + 1
            errors.append(f"Рядок {line_num}: Недопустимий символ '{char}'")
            if len(errors) >= 5:
                errors.append("... (ще є помилки)")
                break
    return errors


def _check_config_content(content: bytes) -> list:
    errors = []

    if not content or not content.strip():
        return ["Файл налаштувань порожній"]

    char_errors = _check_invalid_chars(content, ALLOWED_CONFIG_CHARS)
    if char_errors:
        return char_errors

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return ["Невірне кодування файлу налаштувань"]

    if not text.strip():
        return ["Файл налаштувань порожній"]

    lines = text.split("\n")
    found_keys = set()

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        if "=" not in line:
            errors.append(f"Рядок {i}: Відсутній знак '='")
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key not in VALID_CONFIG_KEYS:
            errors.append(f"Рядок {i}: Невідомий параметр '{key}'")
        else:
            found_keys.add(key)

            if not value:
                errors.append(f"Рядок {i}: Параметр '{key}' не має значення")

        if len(errors) >= 10:
            errors.append("... (ще є помилки)")
            break

    missing_keys = VALID_CONFIG_KEYS - found_keys
    if missing_keys:
        errors.append(
            f"Відсутні обов'язкові параметри: {', '.join(sorted(missing_keys))}"
        )

    return errors


def _check_routes_content(content: bytes) -> list:
    errors = []

    if not content or not content.strip():
        return ["Файл маршрутів порожній"]

    char_errors = _check_invalid_chars(content, ALLOWED_CHARS)
    if char_errors:
        errors.extend(char_errors)
        return errors

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return ["Невірне кодування файлу маршрутів"]

    if not text.strip():
        return ["Файл маршрутів порожній"]

    lines = text.split("\n")
    current_route = None
    expecting_route = False
    expecting_route_line = 0
    has_routes = False

    for i, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("|"):
            if expecting_route:
                errors.append(
                    f"Рядок {i}: Роздільник '|' без номера маршруту перед ним (рядок {expecting_route_line})"
                )
            expecting_route = True
            expecting_route_line = i
            current_route = None
            continue

        if expecting_route:
            if "#" in line:
                route_num_line = line.split("#", 1)[0].strip()
            else:
                route_num_line = line

            if route_num_line.endswith("-"):
                route_num_line = route_num_line[:-1].strip()

            if not route_num_line:
                errors.append(f"Рядок {i}: Порожній номер маршруту після роздільника")
            else:
                current_route = route_num_line
                has_routes = True
            expecting_route = False
            continue

        if not current_route:
            errors.append(f"Рядок {i}: Дані напрямку без номера маршруту")
            continue

        parts = [p.strip() for p in line.split(",")]
        if len(parts) not in (3, 4):
            errors.append(
                f"Рядок {i}: Очікується 3 або 4 значення через кому, отримано {len(parts)}"
            )
            continue

        d_id, p_id, full_name_str = parts[0], parts[1], parts[2]

        if not d_id or not p_id:
            errors.append(
                f"Рядок {i}: Порожній ID напрямку або точки"
            )  ## direction point or something need to be translated better in ukrainian

        if len(parts) == 4:
            short_name_str = parts[3]
            if "^" not in short_name_str:
                errors.append(f"Рядок {i}: Коротка назва має містити роздільник '^'")

        if len(errors) >= 10:
            errors.append("... (ще є помилки)")
            break

    if expecting_route:
        errors.append(
            f"Рядок {expecting_route_line}: Роздільник '|' без номера маршруту після нього"
        )

    if not has_routes and not errors:
        errors.append("У файлі не знайдено жодного маршруту")

    return errors


class WebUpdateServer:
    def __init__(
        self,
        ap_name: str,
        ap_ip: str,
        ap_password: str,
        host: str = "0.0.0.0",
        port: int = 80,
    ):
        self.ap_name = ap_name
        self.ap_password = ap_password
        self.ap_ip = ap_ip
        self.host = host
        self.port = port

        self._app = Microdot()
        self._ap = None
        self._running = False
        self._task = None
        self._start_guard = False

        self._register_routes()

    def is_running(self) -> bool:
        return self._running

    def ensure_started(self):
        """Start the server if not already running."""
        if not self._running and not self._task:
            self.start()

    def start(self):
        """Idempotent start"""
        if self._running or self._task or self._start_guard:
            print("Already starting/running.")
            return
        self._start_guard = True
        try:
            self._task = asyncio.create_task(self._start_servertask())
        finally:
            self._start_guard = False

    def stop(self):
        if not self._running:
            print("Not running.")
            return
        asyncio.create_task(self._stop_servertask())

    def _upload_page(self):
        return UPLOAD_HTML, 200, {"Content-Type": "text/html"}

    def _register_routes(self):
        @safe_route(self)
        @self._app.route("/")
        async def index(request):
            return self._upload_page()

        @safe_route(self)
        @self._app.route("/upload", methods=["POST"])
        async def upload(request):
            content_type = request.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                return self._error_response("Непідтримуваний тип файлу")

            boundary = content_type.split("boundary=")[-1]
            parts = request.body.split(b"--" + boundary.encode())

            if "config" not in os.listdir():
                os.mkdir("config")

            files_to_save = {}

            for part in parts:
                if b"Content-Disposition" in part and b"filename=" in part:
                    headers, file_content = part.split(b"\r\n\r\n", 1)
                    file_content = file_content.rsplit(b"\r\n", 1)[0]

                    header_str = headers.decode()

                    name = header_str.split('name="')[1].split('"')[0]
                    filename = header_str.split('filename="')[1].split('"')[0]

                    if not filename:
                        continue

                    if not filename.endswith(".txt"):
                        return self._error_response(
                            f"Дозволені лише .txt файли: '{filename}'"
                        )

                    if name == "config_file" and filename == "config.txt":
                        errors = _check_config_content(file_content)
                        if errors:
                            return self._error_response(
                                f"Помилка у config.txt: {'; '.join(errors)}"
                            )
                        files_to_save["config.txt"] = file_content

                    elif name == "routes_file" and filename == "routes.txt":
                        errors = _check_routes_content(file_content)
                        if errors:
                            return self._error_response(
                                f"Помилка у routes.txt: {'; '.join(errors)}"
                            )
                        files_to_save["routes.txt"] = file_content
                    else:
                        return self._error_response(
                            "Невірний файл: очікується config.txt або routes.txt"
                        )

            # Save all validated files
            if files_to_save:
                saved_files = []
                for fname, content in files_to_save.items():
                    with open("/config/" + fname, "wb") as f:
                        f.write(content)
                    saved_files.append(fname)

                print("Saved files:", saved_files)
                asyncio.create_task(self._delayed_reset())
                return self._success_response(", ".join(saved_files))
            else:
                return self._error_response(
                    "Не завантажено жодного файлу (приймаються лише config.txt та routes.txt)"
                )

    async def _delayed_reset(self):
        await asyncio.sleep(3)
        machine.reset()

    async def _start_ap(self):
        self._ap = network.WLAN(network.AP_IF)
        self._ap.active(True)
        self._ap.config(essid=self.ap_name, password=self.ap_password)
        self._ap.ifconfig((self.ap_ip, "255.255.255.0", self.ap_ip, "8.8.8.8"))

        while not self._ap.active():
            await asyncio.sleep(0.1)

        print("AP started")
        print(f"SSID: {self.ap_name}")
        print("IP address:", self._ap.ifconfig()[0])

    def _success_response(self, files: str):
        html = SUCCESS_HTML.replace("{files}", files)
        return html, 200, {"Content-Type": "text/html"}

    def _error_response(self, message: str):
        html = ERROR_HTML.replace("{message}", message)
        return html, 400, {"Content-Type": "text/html"}

    async def _start_servertask(self):
        try:
            await self._start_ap()
            self._running = True
            print("Starting server...")
            await self._app.start_server(host=self.host, port=self.port)
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self._running = False
            print("Server stopped")
            self._task = None

    async def _stop_servertask(self):
        print("Stopping server...")
        if self._ap and self._ap.active():
            self._ap.active(False)
            print("Access Point stopped.")

        try:
            self._app.shutdown()
        except Exception as e:
            print(f"Error during shutdown: {e}")

        self._running = False
