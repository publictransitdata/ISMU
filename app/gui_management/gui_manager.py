import sys
from gui_management.gui_config import (
    ScreenConfig,
    RouteMenuConfig,
    DirectionMenuConfig,
    MenuStates,
)

if sys.platform != "rp2":
    from lib.sh1106 import SH1106_I2C  # for vs code
    from lib.writer import Writer  # for vs code


class GuiManager:
    def __init__(
        self,
        display: SH1106_I2C,
        writer: Writer,
        screen_config: ScreenConfig,
        route_menu_config: RouteMenuConfig,
        direction_menu_config: DirectionMenuConfig,
    ):
        """
        Initializes the GuiManager with a display and a text writer instance.
        Args:
            display: The display object used for rendering content on the screen.
            writer: The writer object used for rendering text on the screen.
        """
        self._display = display
        self._writer = writer
        self._route_menu_config = route_menu_config
        self._direction_menu_config = direction_menu_config
        self._screen_config = screen_config

    def draw_route_menu(
        self,
        route_menu: list[str],
    ) -> None:
        """
        Draws a route selection menu on the display.
        Args:
            route_menu: A list of strings representing the route names.
        """
        line_height = self._screen_config.font_size + 2
        top_offset = line_height + 3  # 3 = line and two pixel spacing on the sides
        left_offset = 2
        bottom_offset = self._screen_config.height - 1
        top_offset_with_up_arrow = top_offset + self._screen_config.arrow_size + 2
        screen_center_width = int(self._screen_config.width / 2)
        selected_route = self._route_menu_config.selected
        visible_items = self._screen_config.visible_items
        route_menu_length = self._route_menu_config.number_of_options

        self._display.fill(0)
        self.draw_route_header(self._screen_config.width, left_offset, line_height)

        # Calculate the range of menu items (indexes) that will be visible on the screen
        # based on the currently selected item and the maximum number of visible items.
        start_idx = (selected_route // visible_items) * visible_items
        end_idx = min(start_idx + visible_items, route_menu_length)

        self.draw_menu_items(
            route_menu,
            start_idx,
            end_idx,
            line_height,
            top_offset_with_up_arrow,
            left_offset,
            MenuStates.ROUTE_MENU,
        )

        self.draw_arrows(
            screen_center_width,
            top_offset,
            bottom_offset,
            start_idx,
            end_idx,
            MenuStates.ROUTE_MENU,
        )

        self._display.show()

    def draw_direction_menu(self, direction_menu: list[str]) -> None:
        """
        Draws a direction selection menu on the display.
        Args:
            direction_menu: A list of strings representing the direction names.
        """
        line_height = self._screen_config.font_size + 2
        top_offset = line_height + 3  # 3 = line and two pixel spacing on the sides
        left_offset = 2
        bottom_offset = self._screen_config.height - 1
        top_offset_with_up_arrow = top_offset + self._screen_config.arrow_size + 2
        screen_center_width = int(self._screen_config.width / 2)
        route_number = 3
        selected_route = self._direction_menu_config.selected
        visible_items = self._screen_config.visible_items
        direction_menu_length = self._direction_menu_config.number_of_options

        self._display.fill(0)

        self.draw_direction_header(
            self._screen_config.width, left_offset, line_height, route_number
        )

        # Calculate the range of menu items (indexes) that will be visible on the screen
        # based on the currently selected item and the maximum number of visible items.
        start_idx = (selected_route // visible_items) * visible_items
        end_idx = min(start_idx + visible_items, len(direction_menu))

        self.draw_menu_items(
            direction_menu,
            start_idx,
            end_idx,
            line_height,
            top_offset_with_up_arrow,
            left_offset,
            MenuStates.DIRECTION_MENU,
        )

        self.draw_arrows(
            screen_center_width,
            top_offset,
            bottom_offset,
            start_idx,
            end_idx,
            MenuStates.DIRECTION_MENU,
        )

        self._display.show()

    def draw_route_header(self, screen_width: int, left_offset: int, line_height: int):
        """
        Draws the header for the route selection menu.
        Args:
            screen_width: The width of the display.
            left_offset: The horizontal offset for positioning the text of the header.
            line_height: The height of each line of text in pixels.
        """
        self._writer.set_textpos(self._display, 0, left_offset)
        self._writer.printstring("Маршрут:", False)
        self._display.fill_rect(0, line_height + 1, screen_width, 1, 1)

    def draw_direction_header(
        self, screen_width: int, left_offset: int, line_height: int, route_number: int
    ):
        """
        Draws the header for the direction selection menu.
        Args:
            screen_width: The width of the display.
            left_offset: The horizontal offset for positioning the text of the header.
            line_height: The height of each line of text in pixels.
            route_number: The number of the route being displayed.
        """
        self._writer.set_textpos(self._display, 0, left_offset)
        self._writer.printstring(f"Напрямок:      {route_number})", False)
        self._display.fill_rect(0, line_height + 1, screen_width, 1, 1)

    def draw_menu_items(
        self,
        menu: list[str],
        start: int,
        end: int,
        line_height: int,
        top_offset: int,
        left_offset: int,
        menu_type: str,
    ) -> None:
        """
        Draws the menu items on the display.
        Args:
            menu: A list of menu items (strings) to be displayed.
            start: The index of the first item to be displayed.
            end: The index of the last item to be displayed (exclusive).
            line_height: The spacing in pixels between each menu item.
            top_offset: The vertical starting position for the first menu item.
            left_offset: The horizontal offset for positioning the text of menu items.
        """
        config = self._get_menu_config(menu_type)

        for i in range(start, end):
            y = top_offset + (i - start) * line_height
            is_selected = i == config.selected

            if is_selected:
                self._display.fill_rect(0, y, self._screen_config.width, line_height, 1)
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(menu[i], True)
            else:
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(menu[i], False)

    def draw_arrows(
        self,
        center_x: int,
        top_y: int,
        bottom_y: int,
        start_idx: int,
        end_idx: int,
        menu_type: str,
    ) -> None:
        """
        Draws scrolling arrows (up and/or down) on the display if necessary.
        Args:
            center_x: The horizontal center position for the arrows.
            top_y: The vertical position for the "up" arrow.
            bottom_y: The vertical position for the "down" arrow.
            start_idx: The first index of the currently visible menu item.
            end_idx: The last index of the currently visible menu item.
        """
        config = self._get_menu_config(menu_type)

        if start_idx > 0:
            self.draw_arrow(center_x, top_y, self._screen_config.arrow_size, is_up=True)

        if end_idx < config.number_of_options:
            self.draw_arrow(
                center_x, bottom_y, self._screen_config.arrow_size, is_up=False
            )

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
        coef = 1 if is_up else -1
        for i in range(height):
            for j in range(-i * 2, (i * 2) + 1):
                self._display.pixel(x_center + j, y_top + i * coef, 1)

    def navigate_up(self, menu_type: str) -> None:
        """
        Moves the selection up in the menu.
        """
        config = self._get_menu_config(menu_type)
        if config.selected > 0:
            config.selected -= 1

    def navigate_down(self, menu_type: str) -> None:
        """
        Moves the selection down in the menu.
        """
        config = self._get_menu_config(menu_type)
        if config.selected < config.number_of_options - 1:
            config.selected += 1

    def _get_menu_config(self, menu_type: str):
        if menu_type == MenuStates.ROUTE_MENU:
            return self._route_menu_config
        elif menu_type == MenuStates.DIRECTION_MENU:
            return self._direction_menu_config
        else:
            raise ValueError(f"Unknown menu type: {menu_type}")
