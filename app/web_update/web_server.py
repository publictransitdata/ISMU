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
        ap_pswd: str,
        host: str = "0.0.0.0",
        port: int = 80,
        debug=True,
    ):
        self.app = Microdot()
        self.ap = None
        self.host = host
        self.port = port
        self.debug = debug
        self.running = False
        self.task = None
        self.ap_name = ap_name
        self.ap_pswd = ap_pswd

        self._register_routes()

    def _upload_page(self):
        return UPLOAD_HTML, 200, {"Content-Type": "text/html"}

    def _register_routes(self):
        @self.app.route("/")
        async def index(request):
            return self._upload_page()

        @self.app.route("/upload", methods=["POST"])
        async def upload(request):
            content_type = request.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                return self._response("Unsupported Media Type", 415)

            try:
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

            except Exception as e:
                return self._response(f"Internal server error: {e}", 500)

    async def _delayed_reset(self):
        await asyncio.sleep(3)
        machine.reset()

    async def _start_ap(self):
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid=self.ap_name, password=self.ap_pswd)
        while not self.ap.active():
            await asyncio.sleep(0.1)

        print("AP started")
        print(f"SSID: {self.ap_name}")
        print("IP address:", self.ap.ifconfig()[0])

    def _response(self, text, status=200):
        return text, status

    async def _start_servertask(self):
        try:
            await self._start_ap()
            self.running = True
            print("Starting server...")
            await self.app.start_server(host=self.host, port=self.port)
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.running = False
            print("Server stopped")
            self.task = None

    async def _stop_servertask(self):
        print("Stopping server...")
        if self.ap and self.ap.active():
            self.ap.active(False)
            print("Access Point stopped.")

        try:
            self.app.shutdown()
        except Exception as e:
            print(f"Error during shutdown: {e}")

        self.running = False

    def start(self):
        if not self.running:
            self.task = asyncio.create_task(self._start_servertask())
        else:
            print("Server is already running.")

    def stop(self):
        if self.running:
            asyncio.create_task(self._stop_servertask())
