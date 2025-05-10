from machine import Pin, I2C
import sh1106  # type: ignore
from framebuf import FrameBuffer
import writer  # type: ignore
import monotype_font_ukr  # type: ignore
from gui_management import GuiManager, ScreenConfig, RouteMenuState, DirectionMenuState


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

    direction_menu = ["01 вул Енеїда", "02 вул. Балакіна", "03 Центр", "04 Пум пум"]

    screen_config = ScreenConfig()

    screen_config.set_screen_config(
        screen_width, screen_height, font_size, arrow_size, visible_items
    )

    route_menu_state = RouteMenuState()
    route_menu_state.set_route_state(len(route_menu), 0)

    direction_menu_state = DirectionMenuState()
    direction_menu_state.set_direction_state(len(route_menu), 0)

    if (
        screen_config.width == 0
        or screen_config.height == 0
        or screen_config.font_size == 0
        or screen_config.arrow_size == 0
        or screen_config.visible_items == 0
    ):
        print("Screen configuration is not set correctly.")
        exit()

    if route_menu_state.number_of_options == 0:
        print("Route menu configuration is not set correctly.")
        exit()

    if direction_menu_state.number_of_options == 0:
        print("Direction menu configuration is not set correctly.")
        exit()

    gui_manager = GuiManager(
        display, writer, screen_config, route_menu_state, direction_menu_state
    )

    while True:
        gui_manager.handle_buttons(
            btn_menu.value(), btn_up.value(), btn_down.value(), btn_select.value()
        )
        gui_manager.draw_current_screen(route_menu, direction_menu)

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
