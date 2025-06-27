from machine import Pin, I2C
import sh1106  # type: ignore
from framebuf import FrameBuffer
import writer  # type: ignore
from app.gui_management import (
    GuiManager,
    ScreenConfig,
    RouteMenuState,
    DirectionMenuState,
)
from app.routes_loading import RoutesManager, RouteInfo
from app.config_loading import ConfigManager
import uasyncio as asyncio
import time

try:
    from config import lang_ukr, lang_eng  # type: ignore
except ImportError:
    print("Language file is missing.")


if __name__ == "__main__":
    screen_width = 128
    screen_height = 64
    font_size = 13
    arrow_size = 6
    visible_items = 2

    i2c = I2C(0, scl=Pin(1), sda=Pin(0))
    display = sh1106.SH1106_I2C(128, 64, i2c)

    writers = []

    writer_ukr = writer.Writer(display, lang_ukr)
    writer_eng = writer.Writer(display, lang_eng)

    writers.append(writer_ukr)
    writers.append(writer_eng)

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
        screen_width, screen_height, font_size, arrow_size, visible_items
    )

    if (
        screen_config.width == 0
        or screen_config.height == 0
        or screen_config.font_size == 0
        or screen_config.arrow_size == 0
        or screen_config.visible_items == 0
    ):
        print("Screen configuration is not set correctly.")
        exit()

    async def main_loop(gui: GuiManager):
        while True:
            gui_manager.handle_buttons(
                btn_menu.value(), btn_up.value(), btn_down.value(), btn_select.value()
            )
            gui_manager.draw_current_screen()
            await asyncio.sleep(0.05)

    gui_manager = GuiManager(display, writers, screen_config)
    asyncio.run(main_loop(gui_manager))
