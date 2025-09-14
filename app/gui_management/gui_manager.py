import sys
import time

from app.routes_loading import RoutesManager
from app.config_loading import ConfigManager
from app.web_update import WebUpdateServer
from tinydb import TinyDB, where
from .gui_drawer import GuiDrawer
from app.db_manager import DBManager
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
            writer: The writer object used for rendering string_line on the screen.
            screen_config: Configuration for the screen dimensions and properties.
        """
        self._routes_manager = RoutesManager()
        self._config_manager = ConfigManager()
        self._db_manager = DBManager()
        self._route_menu_state = RouteMenuState()
        self._direction_menu_state = DirectionMenuState()
        self._screen_config = screen_config
        self._web_update_server = WebUpdateServer(
            self._config_manager.config.ap_name, self._config_manager.config.ap_password
        )
        self._gui_drawer = GuiDrawer(display, writer, screen_config)

        self._buttons_press_start_time = None
        self._buttons_press_active = False

    def draw_current_screen(self):
        current_screen = self._screen_config.current_screen

        if current_screen == ScreenStates.ROUTE_MENU:
            menu_items = self.get_route_list_to_display()
            highlighted_item_index = self._get_menu_state(
                ScreenStates.ROUTE_MENU
            )._highlighted_item_index
            number_of_menu_items = self.get_number_of_menu_items()
            self._gui_drawer._draw_menu(
                menu_items, "Маршрут:", highlighted_item_index, number_of_menu_items
            )
        elif current_screen == ScreenStates.DIRECTION_MENU:
            route = self._routes_manager.get_route_by_index(
                self._route_menu_state.highlighted_item_index
            )
            menu_items = self.get_direction_list_to_display(route)
            highlighted_item_index = self._get_menu_state(
                ScreenStates.DIRECTION_MENU
            )._highlighted_item_index
            number_of_menu_items = self.get_number_of_menu_items()
            self._gui_drawer._draw_menu(
                menu_items,
                "Напрямок:",
                highlighted_item_index,
                number_of_menu_items,
                f"   {route['route_number']}",
            )

        elif current_screen == ScreenStates.STATUS_SCREEN:
            route = self._routes_manager.get_route_by_index(
                self._route_menu_state.selected_item_index
            )
            selected_direction_name = route["dirs"][
                self._direction_menu_state.selected_item_index
            ]["full_name"]
            self._gui_drawer.draw_status_screen(
                selected_direction_name,
                route["route_number"],
                self._direction_menu_state.selected_item_index + 1,
                int(
                    route["dirs"][self._direction_menu_state.selected_item_index][
                        "point_id"
                    ]
                ),
            )
        elif current_screen == ScreenStates.ERROR_SCREEN:
            self._gui_drawer.draw_error_screen("Error: Test error message")
        elif current_screen == ScreenStates.SETTINGS_SCREEN:
            self._gui_drawer.draw_active_settings_screen(self._config_manager.config)
        elif current_screen == ScreenStates.UPDATE_SCREEN:
            self._gui_drawer.draw_update_mode_screen(
                self._config_manager.config.ap_ip, self._config_manager.config.ap_name
            )

    def navigate_up(self, menu_type: ScreenStates) -> None:
        menu_state = self._get_menu_state(menu_type)
        if menu_state.highlighted_item_index > 0:
            menu_state.highlighted_item_index -= 1

    def navigate_down(self, menu_type: ScreenStates) -> None:
        menu_state = self._get_menu_state(menu_type)
        get_number_of_menu_items = self.get_number_of_menu_items()

        if menu_state.highlighted_item_index < get_number_of_menu_items - 1:
            menu_state.highlighted_item_index += 1

    def _get_menu_state(
        self, menu_type: ScreenStates
    ) -> RouteMenuState | DirectionMenuState:
        if menu_type == ScreenStates.ROUTE_MENU:
            return self._route_menu_state
        elif menu_type == ScreenStates.DIRECTION_MENU:
            return self._direction_menu_state
        else:
            raise ValueError(f"Unknown menu type: {menu_type}")

    def _check_buttons_press_timer(
        self,
        buttons_pressed: list[int],
        current_screen: str,
        target_screen: str,
        current_time,
    ) -> bool:
        """
        Handles the timer logic for buttons press of any set of buttons.

        Returns:
            True if screen was changed and no further handling is needed.
        """
        all_pressed = all(not b for b in buttons_pressed)

        if all_pressed:
            if not self._buttons_press_active:
                self._buttons_press_start_time = current_time
                self._buttons_press_active = True
            elif time.ticks_diff(current_time, self._buttons_press_start_time) >= 3000:
                if self._screen_config.current_screen == current_screen:
                    self._screen_config.current_screen = target_screen
                self._buttons_press_active = False
                time.sleep(0.5)
            return True
        else:
            self._buttons_press_active = False
            self._buttons_press_start_time = None
            return False

    def handle_buttons(
        self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int
    ) -> None:
        """
        Args:
            btn_menu: The button for toggling between menus.
            btn_up: The button for navigating up in the menu.
            btn_down: The button for navigating down in the menu.
            btn_select: The button for selecting an item in the menu.
        """
        current_time = time.ticks_ms()

        if not btn_up and not btn_down:
            if self._check_buttons_press_timer(
                [btn_up, btn_down],
                ScreenStates.STATUS_SCREEN,
                ScreenStates.SETTINGS_SCREEN,
                current_time,
            ):
                return

        if not btn_down and not btn_select:
            if self._check_buttons_press_timer(
                [btn_down, btn_select],
                ScreenStates.SETTINGS_SCREEN,
                ScreenStates.UPDATE_SCREEN,
                current_time,
            ):
                if self._screen_config.current_screen == ScreenStates.UPDATE_SCREEN:
                    self._web_update_server.ensure_started()
                return

        if not btn_menu:
            if self._screen_config.current_screen == ScreenStates.STATUS_SCREEN:
                self._screen_config.current_screen = ScreenStates.ROUTE_MENU
            elif self._screen_config.current_screen == ScreenStates.ROUTE_MENU:
                self._screen_config.current_screen = ScreenStates.STATUS_SCREEN
            elif self._screen_config.current_screen == ScreenStates.DIRECTION_MENU:
                self._screen_config.current_screen = ScreenStates.ROUTE_MENU
            elif self._screen_config.current_screen == ScreenStates.SETTINGS_SCREEN:
                self._screen_config.current_screen = ScreenStates.STATUS_SCREEN
            elif self._screen_config.current_screen == ScreenStates.UPDATE_SCREEN:
                if self._check_buttons_press_timer(
                    [btn_menu],
                    ScreenStates.UPDATE_SCREEN,
                    ScreenStates.STATUS_SCREEN,
                    current_time,
                ):
                    if self._screen_config.current_screen == ScreenStates.STATUS_SCREEN:
                        self._web_update_server.stop()
                    return
            time.sleep(0.2)

        if not btn_up:
            if self._screen_config.current_screen in (
                ScreenStates.ROUTE_MENU,
                ScreenStates.DIRECTION_MENU,
            ):
                self.navigate_up(self._screen_config.current_screen)
            if self._screen_config.current_screen == ScreenStates.STATUS_SCREEN:
                self._screen_config.current_screen = ScreenStates.DIRECTION_MENU
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
                self._direction_menu_state.highlighted_item_index = 0
            elif self._screen_config.current_screen == ScreenStates.DIRECTION_MENU:
                self._route_menu_state.selected_item_index = (
                    self._route_menu_state.highlighted_item_index
                )
                self._direction_menu_state.selected_item_index = (
                    self._direction_menu_state.highlighted_item_index
                )

                self._screen_config.current_screen = ScreenStates.STATUS_SCREEN
            time.sleep(0.2)

        self._buttons_press_active = False
        self._buttons_press_start_time = None

    def get_route_list_to_display(self) -> list[str]:
        def format_route(route_doc):
            dirs = route_doc.get("dirs", [])
            if not dirs:
                return route_doc["route_number"]
            first_dir = dirs[0]
            label = first_dir.get("short_name") or first_dir.get("full_name", "")
            return f"{route_doc['route_number']} {label}"

        return self._db_manager.with_db(
            lambda db: [format_route(doc) for doc in db.table("routes").all()]
        )

    def get_direction_list_to_display(self, route) -> list[str]:
        menu_items = []
        for d in route.get("dirs", []):
            name = d.get("short_name") or d.get("full_name", "")

            if name and "-" in name:
                parts = name.split("-", 1)
                name = parts[1] if len(parts) > 1 else name

            menu_items.append(f"{d.get('direction_id')} {name}")
        return menu_items

    def get_number_of_menu_items(self) -> int:
        if self._screen_config.current_screen == ScreenStates.ROUTE_MENU:
            return self._routes_manager.get_length_of_routes()
        elif self._screen_config.current_screen == ScreenStates.DIRECTION_MENU:
            return self._routes_manager.get_length_of_directions(
                self._route_menu_state.highlighted_item_index
            )
        else:
            return 0
