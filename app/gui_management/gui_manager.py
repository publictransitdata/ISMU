from lib.sh1106 import SH1106_I2C
from lib.writer import Writer


class GuiManager:
    def __init__(self, display: SH1106_I2C, writer: Writer):
        """
        Initializes the GuiManager with a display and a text writer instance.
        Args:
            display: The display object used for rendering content on the screen.
            writer: The writer object used for rendering text on the screen.
        """
        self._display = display
        self._writer = writer

    def draw_route_menu(
        self,
        routeMenu: list[str],
        screen_width: int,
        screen_height: int,
        font_size: int,
        arrow_size=6,
        visible_items=2,
        selected=0,
    ) -> None:
        """
        Draws a route selection menu on the display.
        Args:
            routeMenu: A list of strings representing the route names.
            screen_width: The width of the display screen in pixels.
            screen_height: The height of the display screen in pixels.
            font_size: The size of the font used for rendering text in the menu.
            arrow_size: The size of the arrows indicating navigation options. Default is 6.
            visible_items: The number of menu items visible at one time. Default is 2.
            selected: The index of the currently selected route. Default is 0.
        """
        line_height = font_size + 2
        top_offset = line_height + 3
        left_offset = 2
        top_offset_with_up_arrow = top_offset + arrow_size + 1
        visible_items = visible_items
        top_offset_with_up_arrow_and_routes = (
            top_offset_with_up_arrow + line_height * visible_items
        )
        screen_center_width = int(screen_width / 2)

        self._display.fill(0)

        # Header
        self._writer.set_textpos(self._display, 0, left_offset)
        self._writer.printstring("Маршрут:", 0)
        self._display.fill_rect(0, 16, screen_width, 1, 1)

        for i in range(visible_items):
            idx = selected + i
            if idx >= len(routeMenu):
                break

            y = top_offset_with_up_arrow + i * line_height
            is_selected = i == 0

            if is_selected:
                self._display.fill_rect(0, y, screen_width, line_height, 1)
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(routeMenu[idx], 1)
            else:
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(routeMenu[idx], 0)

        if selected > 1:
            self.draw_up_arrow(screen_center_width, top_offset, 6, 2)

        if selected + visible_items < len(routeMenu):
            self.draw_down_arrow(
                screen_center_width, top_offset_with_up_arrow_and_routes, 6, 2
            )

        self._display.show()

    def draw_up_arrow(
        self, x_center: int, y_top: int, height=6, width_coefficient=2
    ) -> None:
        """
        Draws an upward-pointing arrow on the display.
        Args:
            x_center: The horizontal center of the arrow.
            y_top: The vertical starting position (top) of the arrow.
            height: The height of the arrow in pixels. Default is 6.
            width_coefficient: Controls the width of the arrow. Default is 2.
        """
        for i in range(height):
            for j in range((-i * width_coefficient), (i * width_coefficient) + 1):
                self._display.pixel(x_center + j, y_top + i, 1)

    def draw_down_arrow(
        self, x_center: int, y_top: int, height=6, width_coefficient=2
    ) -> None:
        """
        Draws a downward-pointing arrow on the display.
        Args:
            x_center: The horizontal center of the arrow.
            y_top: The vertical starting position (top) of the arrow.
            height: The height of the arrow in pixels. Default is 6.
            width_coefficient: Controls the width of the arrow. Default is 2.
        """
        for i in range(height):
            for j in range(
                -(height - i - 1) * width_coefficient,
                (height - i - 1) * width_coefficient + 1,
            ):
                self._display.pixel(x_center + j, y_top + i, 1)
