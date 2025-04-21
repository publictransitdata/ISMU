from machine import Pin, I2C
from lib import sh1106
from framebuf import FrameBuffer
from lib import writer
from lib import monotype_font_ukr
from gui_management import GuiManager




if __name__ == "__main__":
    i2c = I2C(0, scl=Pin(1), sda=Pin(0))
    display = sh1106.SH1106_I2C(128, 64, i2c)

    writer = writer.Writer(display, monotype_font_ukr)

    routeMenu = ["20 Кільцевий", "27 Енеїда"]
    selected = 1

    gui_manager = GuiManager(display, writer)

    gui_manager.draw_route_menu(routeMenu, selected)