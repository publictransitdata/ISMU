from machine import Pin, I2C, UART
import sh1106  # type: ignore
from framebuf import FrameBuffer
import writer  # type: ignore
from app.gui_management import (
    GuiManager,
    ScreenConfig,
    RouteMenuState,
    TripMenuState,
    ScreenStates,
)
from app.routes_management import RoutesManager
from app.config_management import ConfigManager
from app.ibis_management import IBISManager
import uasyncio as asyncio
import time
import gc
import os


try:
    from config import lang  # type: ignore
except ImportError:
    print("Language file is missing.")

CONFIG_PATH = "/config/config.txt"
ROUTES_PATH = "/config/routes.txt"


def check_required_files(*paths):
    missing = set()
    for path in paths:
        try:
            os.stat(path)
        except OSError:
            missing.add(path)

    if CONFIG_PATH in missing and ROUTES_PATH in missing:
        screen_config.current_screen = ScreenStates.INITIAL_SCREEN
        screen_config._is_system_fresh = True


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

    screen_config = ScreenConfig()

    config_manager = ConfigManager()
    routes_manager = RoutesManager()

    check_required_files(CONFIG_PATH, ROUTES_PATH)

    if screen_config.current_screen is not ScreenStates.INITIAL_SCREEN:
        try:
            config_manager.load_config(CONFIG_PATH)
            routes_manager.load_routes(ROUTES_PATH)
        except Exception as e:
            print(f"Error during loading: {e}")

    config_manager.get_current_configuration().load_from_saved_state()

    btn_down = Pin(2, Pin.IN, Pin.PULL_UP)
    btn_select = Pin(3, Pin.IN, Pin.PULL_UP)
    btn_menu = Pin(4, Pin.IN, Pin.PULL_UP)
    btn_up = Pin(5, Pin.IN, Pin.PULL_UP)

    screen_config.set_screen_config(
        screen_width,
        screen_height,
        font_size,
        arrow_size,
        max_menu_items,
        max_number_of_characters_in_line,
    )

    uart = UART(
        0,
        tx=Pin(0),
        rx=Pin(1),
        baudrate=config_manager.config.baudrate,
        bits=config_manager.config.bits,
        parity=config_manager.config.parity,
        stop=config_manager.config.stop,
    )

    if screen_config.current_screen is not ScreenStates.ERROR_SCREEN:
        ibis_manager = IBISManager(uart, config_manager.get_telegram_types())

    gui_manager = GuiManager(display, writer, screen_config)

    async def gui_loop(gui: GuiManager):
        while True:
            gui_manager.handle_buttons(
                btn_menu.value(), btn_up.value(), btn_down.value(), btn_select.value()
            )
            gui_manager.draw_current_screen()
            await asyncio.sleep(0.01)

    async def main_loop():
        if screen_config.current_screen is not ScreenStates.ERROR_SCREEN:
            gui_task = asyncio.create_task(gui_loop(gui_manager))
            ibis_manager.start()
            await asyncio.gather(gui_task, ibis_manager.task)
        else:
            gui_task = asyncio.create_task(gui_loop(gui_manager))
            await asyncio.gather(gui_task)

    asyncio.run(main_loop())
