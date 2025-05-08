from machine import Pin, I2C
import sh1106  # type: ignore
from framebuf import FrameBuffer
import writer  # type: ignore
import monotype_font_ukr  # type: ignore
from gui_management import (
    GuiManager,
    ScreenConfig,
    RouteMenuConfig,
    DirectionMenuConfig,
    MenuStates,
)
import time


if __name__ == "__main__":
    screen_width = 128
    screen_height = 64
    font_size = 13
    arrow_size = 6
    visible_items = 2

    i2c = I2C(0, scl=Pin(1), sda=Pin(0))
    display = sh1106.SH1106_I2C(128, 64, i2c)

    writer = writer.Writer(display, monotype_font_ukr)

    # routes_path = "app/config/routes.txt"
    # routes = Routes()
    # routes.load_routes(routes_path)
    # loaded_routes = routes.get_routes()

    btn_down = Pin(2, Pin.IN, Pin.PULL_UP)
    btn_select = Pin(3, Pin.IN, Pin.PULL_UP)
    btn_menu = Pin(4, Pin.IN, Pin.PULL_UP)
    btn_up = Pin(5, Pin.IN, Pin.PULL_UP)

    route_menu = ["20 Кільцевий", "27 Енеїда", "Пум пум пум", "Агаааа", "Прийом"]

    screen_config = ScreenConfig(
        screen_width, screen_height, font_size, arrow_size, visible_items
    )

    route_menu_config = RouteMenuConfig(len(route_menu), 0)
    direction_menu_config = DirectionMenuConfig(len(route_menu), 0)

    gui_manager = GuiManager(
        display, writer, screen_config, route_menu_config, direction_menu_config
    )

    while True:
        if not btn_menu.value():
            print("Main Menu")
            time.sleep(0.2)
        if not btn_up.value():
            gui_manager.navigate_up(MenuStates.ROUTE_MENU)
            time.sleep(0.2)
        if not btn_down.value():
            gui_manager.navigate_down(MenuStates.ROUTE_MENU)
            time.sleep(0.2)
        if not btn_select.value():
            print("Accepted")
            time.sleep(0.2)

        gui_manager.draw_route_menu(route_menu)


# if __name__ == "__main__":
#     routes_path = "app/config/routes.txt"
#     routes = Routes()
#     routes.load_routes(routes_path)
#     loaded_routes = routes.get_routes()

#     for route in loaded_routes:
#         print(f"Route Number: {route.route_number}")
#         for direction in route.directions:
#             print(f"  group_id ID: {direction.group_id}")
#             print(f"  Point ID: {direction.point_id}")
#             print(f"  Full Names: {direction.full_names}")
#             print(f"  Short Names: {direction.short_names}")
