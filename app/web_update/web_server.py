import gc
import os

import machine
import network
import uasyncio as asyncio
import ujson as json
from microdot import Microdot  # type: ignore

from app.error_codes import ErrorCodes
from app.selection_management import SelectionManager
from app.web_update.safe_route_decorator import safe_route
from utils.error_handler import set_error_and_raise

ALLOWED_ROUTES_CHARS = set(
    " []{}!\"'+,-./0123456789:<=>?ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_abcdefghijklmnopqrstuvwxyz()"
    "ÓóĄąĆćĘęŁłŚśŻżЄІЇАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзийклмнопрстуфхцчшщьюяєії^#|\n\r,+"
)

ALLOWED_CONFIG_CHARS = set(" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_=.-\n\r")


VALID_CONFIG_KEYS = {
    "line_telegram",
    "destination_number_telegram",
    "destination_telegram",
    "show_start_and_end_stops",
    "force_short_names",
    "stop_board_telegram",
    "show_info_on_stop_board",
    "ap_name",
    "ap_password",
    "ap_ip",
    "baudrate",
    "bits",
    "parity",
    "stop",
}


def _get_base_style():
    return """body {
  font-family: Arial;
  margin: 0;
  padding: 0;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}
.c {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 90%;
  text-align: center;
}
h1 {
  font-size: 1.5em;
  margin-bottom: 1em;
}
"""


def _get_upload_html():
    return (
        """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Завантажити</title>
    <style>
      """
        + _get_base_style()
        + """p {
        margin: 0.5em 0 0.2em;
        text-align: left;
      }
      input[type="file"] {
        width: 100%;
      }
      input[type="submit"] {
        margin-top: 1em;
        width: 100%;
        padding: 0.7em;
        font-size: 1em;
        background: #4caf50;
        color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      }
    </style>
  </head>
  <body>
    <div class="c">
      <h1>Режим оновлення</h1>
      <form action="/upload" method="post" enctype="multipart/form-data">
        <p>Завантажити config.txt:</p>
        <input type="file" name="config_file" />
        <p>Завантажити routes.ndjson:</p>
        <input type="file" name="routes_file" />
        <input type="submit" value="Завантажити" />
      </form>
    </div>
  </body>
</html>
"""
    )


def _get_success_html(files: str):
    return (
        """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Успіх</title>
    <style>
      """
        + _get_base_style()
        + """.ok {
        color: #4caf50;
        font-size: 3em;
      }
      p {
        margin: 1em 0;
      }
    </style>
  </head>
  <body>
    <div class="c">
      <div class="ok">&#10004;</div>
      <h1>Успішно завантажено</h1>
      <p>Збережені файли: """
        + files
        + """</p>
      <p>Пристрій перезавантажиться...</p>
    </div>
  </body>
</html>
"""
    )


def _get_error_html(message: str):
    return (
        """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Помилка</title>
    <style>
      """
        + _get_base_style()
        + """.err {
        color: #f44336;
        font-size: 3em;
      }
      p {
        margin: 1em 0;
      }
      a {
        display: inline-block;
        margin-top: 1em;
        padding: 0.5em 1em;
        background: #4caf50;
        color: #fff;
        text-decoration: none;
        border-radius: 4px;
      }
    </style>
  </head>
  <body>
    <div class="c">
      <div class="err">&#10008;</div>
      <h1>Помилка</h1>
      <p>"""
        + message
        + """</p>
      <a href="/">Спробувати ще раз</a>
    </div>
  </body>
</html>
"""
    )


TMP_RAW = "config/tmp_raw.bin"
TMP_CONFIG = "config/tmp_config.txt"
TMP_ROUTES = "config/tmp_routes.ndjson"
STREAM_CHUNK = 1024


def _cleanup_tmp():
    for p in (TMP_RAW, TMP_CONFIG, TMP_ROUTES):
        try:
            os.remove(p)
        except OSError:
            pass


def _check_invalid_chars_file(filepath: str, allowed_chars: set) -> list:
    errors = []
    line_num = 1
    char_index = 0
    try:
        with open(filepath) as f:
            while True:
                chunk = f.read(128)
                if not chunk:
                    break
                for ch in chunk:
                    if ch == "\n":
                        line_num += 1
                    elif ch == "\r":
                        pass
                    elif ch not in allowed_chars:
                        errors.append(f"Рядок {line_num}: Недопустимий символ '{ch}'")
                        if len(errors) >= 5:
                            errors.append("... (ще є помилки)")
                            return errors
                    char_index += 1
    except UnicodeDecodeError as err:
        return [f"Невірне кодування файлу (позиція {err.start})"]
    return errors


def _file_is_empty(filepath: str) -> bool:
    try:
        s = os.stat(filepath)
        if s[6] == 0:
            return True
    except OSError:
        return True
    with open(filepath) as f:
        while True:
            chunk = f.read(128)
            if not chunk:
                return True
            if chunk.strip():
                return False


def _check_config_content_file(filepath: str) -> list:
    errors = []

    if _file_is_empty(filepath):
        return ["Файл налаштувань порожній"]

    char_errors = _check_invalid_chars_file(filepath, ALLOWED_CONFIG_CHARS)
    if char_errors:
        return char_errors

    found_keys = set()
    line_num = 0
    with open(filepath) as f:
        while True:
            line = f.readline()
            if not line:
                break
            line_num += 1
            line = line.strip()
            if not line:
                continue

            if "=" not in line:
                errors.append(f"Рядок {line_num}: Відсутній знак '='")
                if len(errors) >= 10:
                    errors.append("... (ще є помилки)")
                    break
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key not in VALID_CONFIG_KEYS:
                errors.append(f"Рядок {line_num}: Невідомий параметр '{key}'")
            else:
                found_keys.add(key)
                nullable_telegram_keys = {
                    "line",
                    "destination_number",
                    "destination",
                    "stop_board_telegram",
                }

                if not value and key not in nullable_telegram_keys:
                    errors.append(f"Рядок {line_num}: Параметр '{key}' не має значення")

            if len(errors) >= 10:
                errors.append("... (ще є помилки)")
                break

    missing_keys = VALID_CONFIG_KEYS - found_keys
    if missing_keys:
        errors.append(f"Відсутні обов'язкові параметри: {', '.join(sorted(missing_keys))}")

    return errors


def _check_routes_content_file(filepath: str) -> list:
    errors = []

    if _file_is_empty(filepath):
        return ["Файл маршрутів порожній"]

    char_errors = _check_invalid_chars_file(filepath, ALLOWED_ROUTES_CHARS)
    if char_errors:
        return char_errors

    current_route_id = None
    current_route_has_dirs = False
    current_route_line = None
    has_routes = False
    line_num = 0
    seen_route_ids = set()
    seen_p_ids = set()

    def _check_type(value, expected_type: type, field: str):
        if value is None:
            return
        if not isinstance(value, expected_type):
            errors.append(f"Рядок {line_num}: Поле '{field}' має неправильні дані")

    def _require_field(rec, field: str):
        if field not in rec:
            errors.append(f"Рядок {line_num}: Відсутній '{field}'")
            return None
        return rec[field]

    def _check_list_of_str(value, field: str):
        if value is None:
            return
        if not isinstance(value, list):
            errors.append(f"Рядок {line_num}: Поле '{field}' має бути списком")
            return
        for item in value:
            if not isinstance(item, str):
                errors.append(f"Рядок {line_num}: Поле '{field}' має містити лише рядки")
                return

    with open(filepath) as f:
        for line in f:
            line_num += 1
            try:
                rec = json.loads(line)
            except Exception:
                continue

            for key in rec:
                if line.count('"' + key + '":') > 1:
                    errors.append(f"Рядок {line_num}: Дублікат ключа '{key}'")
                    break

            if "id" in rec and "did" in rec:
                errors.append(f"Рядок {line_num}: Запис містить одночасно 'id' та 'did'")
                break
            elif "id" not in rec and "did" not in rec:
                errors.append(f"Рядок {line_num}: Невідомий тип запису (немає 'id' або 'did')")
                break

            if "id" in rec:
                unknown = set(rec) - {"id", "r", "nlt", "note"}
                if unknown:
                    errors.append(f"Рядок {line_num}: Невідомі поля: {', '.join(sorted(unknown))}")
                if current_route_id is not None and not current_route_has_dirs:
                    errors.append(f"Рядок {current_route_line}: Маршрут не має жодного напрямку")
                _check_type(rec["id"], int, "id")
                _check_type(_require_field(rec, "r"), str, "r")
                if "nlt" in rec:
                    _check_type(rec["nlt"], bool, "nlt")
                if "note" in rec:
                    _check_type(rec["note"], str, "note")
                if rec["id"] in seen_route_ids:
                    errors.append(f"Рядок {line_num}: Дублікат id маршруту '{rec['id']}'")
                else:
                    seen_route_ids.add(rec["id"])
                current_route_id = rec["id"]
                current_route_has_dirs = False
                current_route_line = line_num

            if "did" in rec:
                unknown = set(rec) - {"did", "p", "f", "s"}
                if unknown:
                    errors.append(f"Рядок {line_num}: Невідомі поля: {', '.join(sorted(unknown))}")
                _check_type(rec["did"], int, "did")

                _check_type(_require_field(rec, "p"), int, "p")

                _check_list_of_str(_require_field(rec, "f"), "f")
                if "s" in rec:
                    _check_list_of_str(rec["s"], "s")

                if "p" in rec:
                    if rec["p"] in seen_p_ids:
                        errors.append(f"Рядок {line_num}: Дублікат індексу напрямку '{rec['p']}'")
                    else:
                        seen_p_ids.add(rec["p"])

                if current_route_id is None:
                    errors.append(f"Рядок {line_num}: Напрямок без заголовку маршруту")
                elif current_route_id != rec["did"]:
                    errors.append(
                        f"Рядок {line_num}: Напрямок не належить маршруту над ним (очікується did={current_route_id})"
                    )
                    if len(errors) >= 10:
                        errors.append("... (ще є помилки)")
                        break

                current_route_has_dirs = True
                has_routes = True

            if len(errors) >= 10:
                errors.append("... (ще є помилки)")
                break

    if current_route_id is not None and not current_route_has_dirs:
        errors.append(f"Рядок {current_route_line}: Маршрут не має жодного напрямку")

    if not has_routes and not errors:
        errors.append("У файлі не знайдено жодного маршруту")

    return errors


async def _stream_body_to_file(request, filepath):
    remaining = request.content_length
    if not remaining or remaining <= 0:
        raise ValueError("No content to read (Content-Length=0)")
    stream = request.stream
    with open(filepath, "wb") as f:
        while remaining > 0:
            chunk_size = min(remaining, STREAM_CHUNK)
            chunk = await stream.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            remaining -= len(chunk)
            del chunk
            gc.collect()


def _parse_disposition(headers_str):
    name = None
    filename = None
    for line in headers_str.split("\n"):
        if "content-disposition" not in line.lower():
            continue
        if 'name="' in line:
            name = line.split('name="')[1].split('"')[0]
        if 'filename="' in line:
            filename = line.split('filename="')[1].split('"')[0]
        break
    return name, filename


def _read_part_headers(f):
    headers_str = ""
    while True:
        hline = f.readline()
        if not hline:
            return headers_str
        decoded = hline.decode("utf-8", "ignore").strip()
        if decoded == "":
            break
        headers_str += decoded + "\n"
    return headers_str


def _extract_parts_from_file(raw_path, boundary_bytes):
    boundary_marker = b"--" + boundary_bytes
    end_marker = boundary_marker + b"--"

    results = []

    with open(raw_path, "rb") as f:
        while True:
            line = f.readline()
            if not line:
                return results
            if line.strip().startswith(boundary_marker):
                break

        while True:
            headers_str = _read_part_headers(f)
            name, filename = _parse_disposition(headers_str)

            if filename and name == "config_file":
                tmp_path = TMP_CONFIG
            elif filename and name == "routes_file":
                tmp_path = TMP_ROUTES
            else:
                tmp_path = None

            out = None
            if tmp_path:
                out = open(tmp_path, "wb")

            prev_line = None
            found_end = False

            while True:
                bline = f.readline()
                if not bline:
                    if prev_line is not None and out:
                        out.write(prev_line)
                    found_end = True
                    break

                bstripped = bline.strip()
                if bstripped.startswith(boundary_marker):
                    if prev_line is not None and out:
                        if prev_line.endswith(b"\r\n"):
                            out.write(prev_line[:-2])
                        elif prev_line.endswith(b"\n"):
                            out.write(prev_line[:-1])
                        else:
                            out.write(prev_line)

                    if bstripped.startswith(end_marker):
                        found_end = True

                    break

                if prev_line is not None and out:
                    out.write(prev_line)
                prev_line = bline

            if out:
                out.close()
            if tmp_path and filename:
                results.append((name, filename, tmp_path))

            gc.collect()

            if found_end:
                break

    return results


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
        gc.collect()
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
        return _get_upload_html(), 200, {"Content-Type": "text/html; charset=utf-8"}

    def _register_routes(self):
        @self._app.errorhandler(413)
        async def payload_too_large(request):
            return self._error_response("Файл занадто великий. Максимум: 24KB", code=413)

        @safe_route(self)
        @self._app.route("/")
        async def index(request):
            return self._upload_page()

        @safe_route(self)
        @self._app.route("/upload", methods=["POST"])
        async def upload(request):
            gc.collect()
            _cleanup_tmp()

            content_type = request.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                return self._error_response("Непідтримуваний тип файлу")

            boundary = content_type.split("boundary=")[-1]

            try:
                await _stream_body_to_file(request, TMP_RAW)
            except Exception as err:
                _cleanup_tmp()
                return self._error_response(f"Помилка при отриманні даних: {err}")

            gc.collect()

            try:
                parts = _extract_parts_from_file(TMP_RAW, boundary.encode())
            except Exception as err:
                _cleanup_tmp()
                return self._error_response(f"Помилка при обробці файлів: {err}")

            try:
                os.remove(TMP_RAW)
            except OSError:
                pass
            gc.collect()

            if "config" not in os.listdir("/"):
                os.mkdir("/config")

            files_to_save = {}

            for name, filename, tmp_path in parts:
                if not filename:
                    continue

                if not filename.endswith((".txt", ".ndjson")):
                    _cleanup_tmp()
                    return self._error_response(f"Дозволені лише .txt і .ndjson файли: '{filename}'")

                if name == "config_file":
                    if "config" in filename.lower():
                        errors = _check_config_content_file(tmp_path)
                        if errors:
                            _cleanup_tmp()
                            return self._error_response(f"Помилка у config.txt: {'; '.join(errors)}")
                        files_to_save["config.txt"] = tmp_path
                    else:
                        _cleanup_tmp()
                        return self._error_response(
                            f'Невірна назва файлу. Очікується файл з "config" у назві (замість {filename})'
                        )

                elif name == "routes_file":
                    if "routes" in filename.lower():
                        errors = _check_routes_content_file(tmp_path)
                        if errors:
                            _cleanup_tmp()
                            return self._error_response(f"Помилка у routes.ndjson: {'; '.join(errors)}")
                        files_to_save["routes.ndjson"] = tmp_path
                    else:
                        _cleanup_tmp()
                        return self._error_response(
                            f'Невірна назва файлу. Очікується файл з "routes" у назві (замість {filename})'
                        )

            if files_to_save:
                saved_files = []
                for fname, tmp_path in files_to_save.items():
                    dest = "/config/" + fname
                    try:
                        os.remove(dest)
                    except OSError:
                        pass
                    os.rename(tmp_path, dest)
                    saved_files.append(fname)

                _cleanup_tmp()
                gc.collect()

                if "routes.ndjson" in saved_files:
                    selection_manager = SelectionManager()
                    selection_manager.reset_selection()

                asyncio.create_task(self._delayed_reset())
                return self._success_response(", ".join(saved_files))
            else:
                _cleanup_tmp()
                return self._error_response("Не завантажено жодного файлу")

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
        return _get_success_html(files), 200, {"Content-Type": "text/html; charset=utf-8"}

    def _error_response(self, message: str, code: int = 400):
        return _get_error_html(message), code, {"Content-Type": "text/html; charset=utf-8"}

    async def _start_servertask(self):
        try:
            await self._start_ap()
            self._running = True
            print("Starting server...")
            await self._app.start_server(host=self.host, port=self.port)
        except Exception as err:
            set_error_and_raise(ErrorCodes.WEB_SERVER_ERROR, err, show_message=True)
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
        except Exception as err:
            set_error_and_raise(ErrorCodes.WEB_SERVER_SHUTDOWN_ERROR, err, show_message=True)

        self._running = False
