from machine import Pin, I2C
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

    i2c = I2C(0, scl=Pin(1), sda=Pin(0))
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

    if (
        screen_config.screen_width == 0
        or screen_config.screen_height == 0
        or screen_config.font_size == 0
        or screen_config.arrow_size == 0
        or screen_config.max_menu_items == 0
        or max_number_of_characters_in_line == 0
    ):
        print("Screen configuration is not set correctly.")
        exit()

    async def main_loop(gui: GuiManager):
        while True:
            gui_manager.handle_buttons(
                btn_menu.value(), btn_up.value(), btn_down.value(), btn_select.value()
            )
            await asyncio.sleep(0.01)

    gui_manager = GuiManager(display, writer, screen_config)
    asyncio.run(main_loop(gui_manager))
