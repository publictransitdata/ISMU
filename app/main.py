from machine import Pin, I2C
import sh1106  # type: ignore
from framebuf import FrameBuffer
import writer  # type: ignore
import monotype_font_ukr  # type: ignore
from gui_management import GuiManager, ScreenConfig, RouteMenuState, DirectionMenuState
from routes_loading import Routes, RouteInfo
import time


def draw_error_screen(display, error_message: str) -> None:
    display.fill(0)
    writer.set_textpos(display, 0, 0)
    writer.printstring(error_message, False)
    display.show()


if __name__ == "__main__":
    screen_width = 128
    screen_height = 64
    font_size = 13
    arrow_size = 6
    visible_items = 2

    i2c = I2C(0, scl=Pin(1), sda=Pin(0))
    display = sh1106.SH1106_I2C(128, 64, i2c)

    writer = writer.Writer(display, monotype_font_ukr)

    routes_path = "/app/config/routes.txt"
    routes = Routes()
    routes.load_routes(routes_path)
    loaded_routes = routes.routes

    # print("Loaded routes:")
    # for route in loaded_routes:
    #     print("Route number:")
    #     print(route.route_number)
    #     print("Directions:")
    #     for direction in route.directions:
    #         print(direction.group_id)

    btn_down = Pin(2, Pin.IN, Pin.PULL_UP)
    btn_select = Pin(3, Pin.IN, Pin.PULL_UP)
    btn_menu = Pin(4, Pin.IN, Pin.PULL_UP)
    btn_up = Pin(5, Pin.IN, Pin.PULL_UP)

    screen_config = ScreenConfig()

    screen_config.set_screen_config(
        screen_width, screen_height, font_size, arrow_size, visible_items
    )

    # route_menu_state = RouteMenuState()
    # route_menu_state.set_route_state(len(routes.routes), 0)

    # direction_menu_state = DirectionMenuState()
    # direction_menu_state.set_direction_state(
    #     len(routes.routes[route_menu_state.selected].directions), 0
    # )

    # route_menu = get_route_menu(routes.routes)

    # # for r in route_menu:

    # #     print(r)

    # direction_menu = get_direction_menu(routes.routes[route_menu_state.selected])

    # for d in direction_menu:
    #     draw_error_screen(display, d)
    #     time.sleep(2)

    if (
        screen_config.width == 0
        or screen_config.height == 0
        or screen_config.font_size == 0
        or screen_config.arrow_size == 0
        or screen_config.visible_items == 0
    ):
        print("Screen configuration is not set correctly.")
        exit()

    gui_manager = GuiManager(display, writer, screen_config)

    while True:
        gui_manager.handle_buttons(
            btn_menu.value(), btn_up.value(), btn_down.value(), btn_select.value()
        )
        gui_manager.draw_current_screen()
