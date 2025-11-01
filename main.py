from machine import Pin, I2C, UART
import sh1106  # type: ignore
from framebuf import FrameBuffer
import writer  # type: ignore
from app.gui_management import (
    GuiManager,
    ScreenConfig,
    RouteMenuState,
    TripMenuState,
)
from app.routes_loading import RoutesManager
from app.config_loading import ConfigManager
from app.ibis_management import IBISManager
import uasyncio as asyncio
import time
import gc

try:
    from config import lang  # type: ignore
except ImportError:
    print("Language file is missing.")


if __name__ == "__main__":
    screen_width = 128
    screen_height = 64
    font_size = 13
    arrow_size = 6
    max_menu_items = 2
    max_number_of_characters_in_line = 18

    i2c = I2C(1, scl=Pin(11), sda=Pin(10))
    display = sh1106.SH1106_I2C(128, 64, i2c)

    writer = writer.Writer(display, lang)

    config_path = "/config/config.txt"
    config = ConfigManager()
    config.load_config(config_path)

    routes_path = "/config/routes.txt"
    routes = RoutesManager()
    routes.load_routes(routes_path)

    btn_down = Pin(2, Pin.IN, Pin.PULL_UP)
    btn_select = Pin(3, Pin.IN, Pin.PULL_UP)
    btn_menu = Pin(4, Pin.IN, Pin.PULL_UP)
    btn_up = Pin(5, Pin.IN, Pin.PULL_UP)

    screen_config = ScreenConfig()

    screen_config.set_screen_config(
        screen_width,
        screen_height,
        font_size,
        arrow_size,
        max_menu_items,
        max_number_of_characters_in_line,
    )

    uart = UART(0, tx=Pin(0), rx=Pin(1), baudrate=1200, bits=7, parity=2, stop=2)

    ibis_manager = IBISManager(uart, config.get_telegram_types())

    gui_manager = GuiManager(display, writer, screen_config)

    async def gui_loop(gui: GuiManager):
        while True:
            gui_manager.handle_buttons(
                btn_menu.value(), btn_up.value(), btn_down.value(), btn_select.value()
            )
            gui_manager.draw_current_screen()
            await asyncio.sleep(0.01)

    async def main_loop():
        gui_task = asyncio.create_task(gui_loop(gui_manager))
        ibis_manager.start()

        await asyncio.gather(gui_task, ibis_manager.task)

    asyncio.run(main_loop())
