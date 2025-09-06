from app.web_update.safe_route_decorator import _safe_route
from microdot import Microdot  # type: ignore
import network
import uasyncio as asyncio
import os
import machine


UPLOAD_HTML = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Upload</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #f5f5f5;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                }
                .container {
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    max-width: 400px;
                    width: 90%;
                }
                h1 {
                    font-size: 1.5em;
                    margin-bottom: 1em;
                    text-align: center;
                }
                p {
                    margin: 0.5em 0 0.2em;
                }
                input[type="file"] {
                    width: 100%;
                }
                input[type="submit"] {
                    margin-top: 1em;
                    width: 100%;
                    padding: 0.7em;
                    font-size: 1em;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background: #45a049;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Upload Mode</h1>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <p>Upload config.txt:</p>
                    <input type="file" name="config_file">
                    <p>Upload routes.txt:</p>
                    <input type="file" name="routes_file">
                    <input type="submit" value="Upload">
                </form>
            </div>
        </body>
        </html>
        """


class WebUpdateServer:
    def __init__(
        self,
        ap_name: str,
        ap_password: str,
        host: str = "0.0.0.0",
        port: int = 80,
    ):
        self.ap_name = ap_name
        self.ap_password = ap_password
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
        @_safe_route(self)
        @self._app.route("/")
        async def index(request):
            return self._upload_page()

        @_safe_route(self)
        @self._app.route("/upload", methods=["POST"])
        async def upload(request):
            content_type = request.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                return self._response("Unsupported Media Type", 415)

            boundary = content_type.split("boundary=")[-1]
            parts = request.body.split(b"--" + boundary.encode())

            if "config" not in os.listdir():
                os.mkdir("config")

            saved_files = []

            for part in parts:
                if b"Content-Disposition" in part and b"filename=" in part:
                    headers, file_content = part.split(b"\r\n\r\n", 1)
                    file_content = file_content.rsplit(b"\r\n", 1)[0]

                    header_str = headers.decode()

                    # Extract name and filename
                    name = header_str.split('name="')[1].split('"')[0]
                    filename = header_str.split('filename="')[1].split('"')[0]

                    # Validation
                    if (name == "config_file" and filename == "config.txt") or (
                        name == "routes_file" and filename == "routes.txt"
                    ):
                        with open("/config/" + filename, "wb") as f:
                            f.write(file_content)
                        saved_files.append(filename)
                    else:
                        return self._response(
                            "Invalid file upload: wrong field or filename", 400
                        )

            if saved_files:
                print("Saved files:", saved_files)
                asyncio.create_task(self._delayed_reset())
                return f"Saved files: {', '.join(saved_files)}"
            else:
                return self._response(
                    "No valid files uploaded (only config.txt or routes.txt are accepted)",
                    400,
                )

    async def _delayed_reset(self):
        await asyncio.sleep(3)
        machine.reset()

    async def _start_ap(self):
        self._ap = network.WLAN(network.AP_IF)
        self._ap.active(True)
        self._ap.config(essid=self.ap_name, password=self.ap_password)
        while not self._ap.active():
            await asyncio.sleep(0.1)

        print("AP started")
        print(f"SSID: {self.ap_name}")
        print("IP address:", self._ap.ifconfig()[0])

    def _response(self, text, status=200):
        return text, status

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
