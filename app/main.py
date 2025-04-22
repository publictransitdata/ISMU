from machine import Pin, I2C
import sh1106
from framebuf import FrameBuffer
import writer
import monotype_font_ukr
from gui_management import GuiManager, ScreenConfig, MenuConfig

if __name__ == "__main__":
    screen_width = 128
    screen_height = 64
    font_size = 13
    arrow_size = 6
    visible_items = 2

    i2c = I2C(0, scl=Pin(1), sda=Pin(0))
    display = sh1106.SH1106_I2C(128, 64, i2c)

    writer = writer.Writer(display, monotype_font_ukr)

    route_menu = ["20 Кільцевий", "27 Енеїда", "Пум пум пум", "Агаааа", "Прийом"]
    selected = 2

    gui_manager = GuiManager(display, writer)

    screen_config = ScreenConfig(screen_width, screen_height, font_size)
    menu_config = MenuConfig(arrow_size, visible_items, selected)

    gui_manager.draw_route_menu(
        route_menu,
        screen_config,
        menu_config
    )
