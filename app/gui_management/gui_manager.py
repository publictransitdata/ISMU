import sh1106
import writer
from gui_management.config import ScreenConfig, MenuConfig


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
        route_menu: list[str],
        screen_config: ScreenConfig,
        menu_config: MenuConfig,
    ) -> None:
        """
        Draws a route selection menu on the display.
        Args:
            route_menu: A list of strings representing the route names.
            screen_config: Configuration object containing screen dimensions and font size.
            menu_config: Configuration object containing menu display settings.
        """
        line_height = screen_config.font_size + 2
        top_offset = line_height + 3  # 3 = line and two pixel spacing on the sides
        left_offset = 2
        bottom_offset = screen_config.height - 1
        top_offset_with_up_arrow = top_offset + menu_config.arrow_size + 2
        screen_center_width = int(screen_config.width / 2)

        self._display.fill(0)

        self.draw_header(screen_config.width, left_offset, line_height)

        # Calculate the range of menu items (indexes) that will be visible on the screen
        # based on the currently selected item and the maximum number of visible items.
        start_idx = (
            menu_config.selected // menu_config.visible_items
        ) * menu_config.visible_items
        end_idx = min(start_idx + menu_config.visible_items, len(route_menu))

        self.draw_menu_items(
            route_menu,
            start_idx,
            end_idx,
            menu_config.selected,
            screen_config.width,
            line_height,
            top_offset_with_up_arrow,
            left_offset=2,
        )

        self.draw_arrows(
            screen_center_width,
            top_offset,
            bottom_offset,
            start_idx,
            end_idx,
            len(route_menu),
            menu_config.arrow_size,
        )

        self._display.show()

    def draw_header(self, screen_width: int, left_offset: int, line_height: int):
        """
        Draws the header section of the menu on the display. The header contains a title and a separator.
        Args:
            screen_width: The width of the display in pixels.
            left_offset: The horizontal offset for the text.
        """
        self._writer.set_textpos(self._display, 0, left_offset)
        self._writer.printstring("Маршрут:", 0)
        self._display.fill_rect(0, line_height + 1, screen_width, 1, 1)

    def draw_menu_items(
        self,
        menu: list[str],
        start: int,
        end: int,
        selected: int,
        screen_width: int,
        line_height: int,
        top_offset: int,
        left_offset: int,
    ) -> None:
        """
        Draws the menu items on the display.
        Args:
            menu: A list of menu items (strings) to be displayed.
            start: The index of the first item to be displayed.
            end: The index of the last item to be displayed (exclusive).
            selected: The index of the currently selected item in the menu.
            screen_width: The width of the display, used to position elements.
            line_height: The spacing in pixels between each menu item.
            top_offset: The vertical starting position for the first menu item.
            left_offset: The horizontal offset for positioning the text of menu items.
        """
        for i in range(start, end):
            y = top_offset + (i - start) * line_height
            is_selected = i == selected

            if is_selected:
                self._display.fill_rect(0, y, screen_width, line_height, 1)
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(menu[i], 1)
            else:
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(menu[i], 0)

    def draw_arrows(
        self,
        center_x: int,
        top_y: int,
        bottom_y: int,
        start_idx: int,
        end_idx: int,
        menu_length: int,
        arrow_size: int,
    ) -> None:
        """
        Draws scrolling arrows (up and/or down) on the display if necessary.
        Args:
            center_x: The horizontal center position for the arrows.
            top_y: The vertical position for the "up" arrow.
            bottom_y: The vertical position for the "down" arrow.
            start_idx: The first index of the currently visible menu item.
            end_idx: The last index of the currently visible menu item.
            menu_length: The total number of items in the menu.
            arrow_size: The size (height) of the arrows in pixels.
        """
        if start_idx > 0:
            self.draw_arrow(center_x, top_y, arrow_size, is_up=True)

        if end_idx < menu_length:
            self.draw_arrow(center_x, bottom_y, arrow_size, is_up=False)

    def draw_arrow(self, x_center: int, y_top: int, height: int, is_up: bool) -> None:
        """
        Draws an arrow (up or down) on the display.
        Args:
            x_center: The horizontal center of the arrow on the display.
            y_top: The vertical starting position of the arrow's tip.
                   For an up arrow, this is the topmost pixel, and the arrow is drawn downward.
                   For a down arrow, this is the bottommost pixel, and the arrow is drawn upward.
            height: The height of the arrow, in pixels.
            is_up: If True, the arrow points upward. If False, the arrow points downward.
        """
        coef = 1 if is_up else -1  # Controls the arrow pointing direction
        for i in range(height):
            for j in range(-i * 2, (i * 2) + 1):
                self._display.pixel(x_center + j, y_top + i * coef, 1)
