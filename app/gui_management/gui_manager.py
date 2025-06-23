import sys
import time

from routes_loading.route_info import RouteInfo
from routes_loading.routes_loader import Routes
from .gui_config import (
    ScreenConfig,
    RouteMenuState,
    DirectionMenuState,
    ScreenStates,
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
    ):
        """
        Initializes the GuiManager with the necessary configurations and display components.

        Args:
            display: The display object used for rendering content on the screen.
            writer: The writer object used for rendering text on the screen.
            screen_config: Configuration for the screen dimensions and properties.
            route_menu_state: State management for the route menu.
            direction_menu_state: State management for the direction menu.
        """
        self._display = display
        self._writer = writer
        self._routes = Routes()
        self._route_menu_state = RouteMenuState()
        self._route_menu_state.set_route_state(0)
        self._direction_menu_state = DirectionMenuState()
        self._direction_menu_state.set_direction_state(0)
        self._screen_config = screen_config

    def _draw_menu(
        self,
        items: list[str],
        menu_type: str,
        header_text: str,
        header_suffix: str = "",
    ) -> None:
        """
        Draws a menu on the display. There is same template for route and direction menus.

        Args:
            items: A list of menu items to display.
            menu_type: The type of menu (e.g., route or direction).
            header_text: The text to display in the menu header.
            header_suffix: Additional text to display in the header. Defaults to an empty string.
        """
        line_height = self._screen_config.font_size + 2
        top_offset = line_height + 3  # 3 = line and two pixel spacing on the sides
        left_offset = 2
        bottom_offset = self._screen_config.height - 1
        top_offset_with_up_arrow = top_offset + self._screen_config.arrow_size + 2
        screen_center_width = int(self._screen_config.width / 2)
        highlighted_index = self._get_menu_state(menu_type).highlighted
        visible_items = self._screen_config.visible_items

        self._display.fill(0)

        self._writer.set_textpos(self._display, 0, left_offset)
        self._writer.printstring(f"{header_text}{header_suffix}", False)
        self._display.fill_rect(0, line_height + 1, self._screen_config.width, 1, 1)

        # Calculate the range of menu items (indexes) that will be visible on the screen
        # based on the currently selected item and the maximum number of visible items.
        start_idx = (highlighted_index // visible_items) * visible_items
        end_idx = min(start_idx + visible_items, len(items))

        self.draw_menu_items(
            items,
            start_idx,
            end_idx,
            line_height,
            top_offset_with_up_arrow,
            left_offset,
            menu_type,
        )

        self.draw_arrows(
            screen_center_width,
            top_offset,
            bottom_offset,
            start_idx,
            end_idx,
        )

        self._display.show()

    def trim_text_to_fit(self, text: str, max_width: int) -> str:
        """
        Trims the input text to fit within the given pixel width.
        If it's too long, shortens it and adds ellipsis.

        Args:
            text (str): The string to trim.
            max_width (int): The maximum width in pixels.

        Returns:
            str: Trimmed string.
        """
        if self._writer.stringlen(text) <= max_width:
            return text

        for i in range(len(text), 0, -1):
            trimmed = text[:i]
            if self._writer.stringlen(trimmed) <= max_width:
                return trimmed

        return "..."

    def draw_current_screen(self):
        """
        Draws the current screen based on the screen state.
        """
        current_screen = self._screen_config.current_screen

        if current_screen == ScreenStates.ROUTE_MENU:
            menu = self.get_route_menu(self._routes.routes)
            self._draw_menu(menu, ScreenStates.ROUTE_MENU, "Маршрут:")
        elif current_screen == ScreenStates.DIRECTION_MENU:
            route = self._routes.routes[self._route_menu_state.highlighted]
            menu = self.get_direction_menu(route)
            self._draw_menu(
                menu,
                ScreenStates.DIRECTION_MENU,
                "Напрямок:",
                f"   {route.route_number}",
            )

        elif current_screen == ScreenStates.STATUS_SCREEN:
            route = self._routes.routes[self._route_menu_state.selected]
            direction_name = route.directions[
                self._direction_menu_state.selected
            ].full_name
            self.draw_status_screen(
                direction_name,
                route.route_number,
                self._direction_menu_state.selected + 1,
                int(route.directions[self._direction_menu_state.selected].point_id),
            )
        elif current_screen == ScreenStates.ERROR_SCREEN:
            self.draw_error_screen("Error: Test error message")

    def draw_status_screen(
        self,
        direction_name: str,
        route_id: str,
        direction_id: int,
        direction_number: int,
    ) -> None:
        """
        Draws the status screen with the selected direction and general selected information.

        Args:
            direction_name (str): The name of the selected direction.
            route_id (str): The ID of the selected route.
            direction_id (int): The ID of the selected direction.
            direction_number (int): The number of the selected direction.
        """
        line_height = self._screen_config.font_size + 2
        left_offset = 2
        screen_height = self._screen_config.height

        self._display.fill(0)

        self._writer.set_textpos(self._display, 0, left_offset)
        self._writer.printstring("> " + direction_name, False)

        bottom_y = screen_height - line_height
        self._writer.set_textpos(self._display, bottom_y, left_offset)
        self._writer.printstring(
            f"М:{route_id}Н:{direction_id:02d}К:{direction_number}",
            False,
        )

        self._display.show()

    def draw_error_screen(self, error_message: str) -> None:
        """
        Draws an error message on the display.

        Args:
            error_message: The error message to display.
        """
        self._display.fill(0)
        self._writer.set_textpos(self._display, 0, 0)
        self._writer.printstring(error_message, False)
        self._display.show()

    def draw_update_mode_screen(self, ip_address: str) -> None:
        """
        Draws the update mode screen with the device's IP address.

        Args:
            ip_address: The IP address to display on the screen.
        """
        self._display.fill(0)

        line_height = self._screen_config.font_size + 2
        screen_width = self._screen_config.width
        screen_height = self._screen_config.height

        line1 = "Режим оновлення"
        line2 = f"ІР: {ip_address}"

        top_y = int((screen_height - line_height * 2) / 2)

        line1_width = self._writer.stringlen(line1)
        line2_width = self._writer.stringlen(line2)

        line1_offset = (screen_width - line1_width) // 2
        line2_offset = (screen_width - line2_width) // 2

        self._writer.set_textpos(self._display, top_y, line1_offset)
        self._writer.printstring(line1, False)

        self._writer.set_textpos(self._display, top_y + line_height + 2, line2_offset)
        self._writer.printstring(line2, False)

        self._display.show()

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
            menu_type: The type of menu being displayed (e.g., route or direction).
        """
        config = self._get_menu_state(menu_type)

        for i in range(start, end):
            y = top_offset + (i - start) * line_height
            is_highlighted = i == config.highlighted
            available_width = self._screen_config.width - left_offset
            text = self.trim_text_to_fit(menu[i], available_width)

            if is_highlighted:
                self._display.fill_rect(0, y, self._screen_config.width, line_height, 1)
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(text, True)
            else:
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(text, False)

    def draw_arrows(
        self,
        center_x: int,
        top_y: int,
        bottom_y: int,
        start_idx: int,
        end_idx: int,
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

        if start_idx > 0:
            self.draw_arrow(center_x, top_y, self._screen_config.arrow_size, is_up=True)

        number_of_options = self.number_of_options()

        if end_idx < number_of_options:
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

        Args:
            menu_type: The type of menu to navigate (e.g., route or direction).
        """
        config = self._get_menu_state(menu_type)
        if config.highlighted > 0:
            config.highlighted -= 1

    def navigate_down(self, menu_type: str) -> None:
        """
        Moves the selection down in the menu.

        Args:
            menu_type: The type of menu to navigate (e.g., route or direction).
        """
        config = self._get_menu_state(menu_type)
        number_of_options = self.number_of_options()

        if config.highlighted < number_of_options - 1:
            config.highlighted += 1

    def _get_menu_state(self, menu_type: str):
        """
        Retrieves the state object for the specified menu type.

        Args:
            menu_type: The type of menu (e.g., route or direction).

        Returns:
            RouteMenuState or DirectionMenuState: The state object for the menu.
        """
        if menu_type == ScreenStates.ROUTE_MENU:
            return self._route_menu_state
        elif menu_type == ScreenStates.DIRECTION_MENU:
            return self._direction_menu_state
        else:
            raise ValueError(f"Unknown menu type: {menu_type}")

    def handle_buttons(
        self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int
    ) -> None:
        """
        Handles button presses and navigates or updates screen state accordingly.

        Args:
            btn_menu: The button for toggling between menus.
            btn_up: The button for navigating up in the menu.
            btn_down: The button for navigating down in the menu.
            btn_select: The button for selecting an item in the menu.
        """
        if not btn_menu:
            if self._screen_config.current_screen == ScreenStates.STATUS_SCREEN:
                self._screen_config.current_screen = ScreenStates.ROUTE_MENU
            elif self._screen_config.current_screen == ScreenStates.ROUTE_MENU:
                self._screen_config.current_screen = ScreenStates.STATUS_SCREEN
            elif self._screen_config.current_screen == ScreenStates.DIRECTION_MENU:
                self._screen_config.current_screen = ScreenStates.ROUTE_MENU
            time.sleep(0.2)

        if not btn_up:
            if self._screen_config.current_screen in (
                ScreenStates.ROUTE_MENU,
                ScreenStates.DIRECTION_MENU,
            ):
                self.navigate_up(self._screen_config.current_screen)
            time.sleep(0.2)

        if not btn_down:
            if self._screen_config.current_screen in (
                ScreenStates.ROUTE_MENU,
                ScreenStates.DIRECTION_MENU,
            ):
                self.navigate_down(self._screen_config.current_screen)
            time.sleep(0.2)

        if not btn_select:
            if self._screen_config.current_screen == ScreenStates.ROUTE_MENU:
                self._screen_config.current_screen = ScreenStates.DIRECTION_MENU
                self._direction_menu_state.highlighted = 0
            elif self._screen_config.current_screen == ScreenStates.DIRECTION_MENU:
                self._route_menu_state.selected = self._route_menu_state.highlighted
                self._direction_menu_state.selected = (
                    self._direction_menu_state.highlighted
                )

                self._screen_config.current_screen = ScreenStates.STATUS_SCREEN
            time.sleep(0.2)

    def get_route_menu(self, routes: list[RouteInfo]) -> list[str]:
        """Extracts route numbers and route names for the menu display."""
        return [
            f"{route.route_number} {(route.directions[0].short_name or route.directions[0].full_name)}"
            for route in routes
        ]

    def get_direction_menu(self, route: RouteInfo) -> list[str]:
        """Extracts direction full names with id for the menu display."""
        return [
            f"{direction.group_id} {direction.full_name.split('-')[1]}"
            for direction in route.directions
        ]

    def number_of_options(self) -> int:
        """
        Returns the number of options in the current menu based on the current screen state.

        Returns:
            int: The number of options in the current menu.
        """
        if self._screen_config.current_screen == ScreenStates.ROUTE_MENU:
            return len(self._routes.routes)
        elif self._screen_config.current_screen == ScreenStates.DIRECTION_MENU:
            return len(
                self._routes.routes[self._route_menu_state.highlighted].directions
            )
        else:
            return 0
