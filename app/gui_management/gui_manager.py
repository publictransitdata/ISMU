import sys
import time

import ujson as json
from app.config_management import ConfigManager
from app.error_codes import ErrorCodes
from app.routes_management import RoutesManager
from app.selection_management import SelectionManager
from app.web_update import WebUpdateServer
from utils.error_handler import set_error_and_raise

from .gui_config import (
    RouteMenuState,
    TripMenuState,
)

from .gui_drawer import GuiDrawer

if sys.platform != "rp2":
    from lib.sh1106 import SH1106_I2C  # for vs code
    from lib.writer import Writer  # for vs code


class ScreenStates:
    STATUS_SCREEN = "status"
    ROUTE_MENU = "route"
    TRIP_MENU = "trip"
    ERROR_SCREEN = "error"
    SETTINGS_SCREEN = "settings"
    UPDATE_SCREEN = "update"
    INITIAL_SCREEN = "initial"
    START_SCREEN = "start"
    MESSAGE_SCREEN = "message"


class State:
    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    def handle_buttons(
        self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int
    ):
        raise NotImplementedError(
            "handle_buttons method should be implemented in the subclass"
        )

    def draw_current_screen(self):
        raise NotImplementedError(
            "draw_current_screen method should be implemented in the subclass"
        )


class StatusState(State):
    def draw_current_screen(self):
        route = self._routes_manager.get_route_by_index(
            self._route_menu_state.selected_item_index
        )
        selected_trip_name_list = route["dirs"][
            self._trip_menu_state.selected_item_index
        ]["full_name"]
        if len(selected_trip_name_list) == 2:
            selected_trip_name = selected_trip_name_list[1]
        else:
            selected_trip_name = selected_trip_name_list[0]
        self._gui_drawer.draw_status_screen(
            selected_trip_name,
            route["route_number"],
            self._trip_menu_state.selected_item_index + 1,
            int(route["dirs"][self._trip_menu_state.selected_item_index]["point_id"]),
        )


class GuiManager:
    def __init__(self, display: SH1106_I2C, writer: Writer):
        """
        Initializes the GuiManager with the necessary configurations and display components.

        Args:
            display: The display object used for rendering content on the screen.
            writer: The writer object used for rendering string_line on the screen.
            screen_config: Configuration for the screen dimensions and properties.
        """
        self._routes_manager = RoutesManager()
        self._config_manager = ConfigManager()
        self._route_menu_state = RouteMenuState()
        self._trip_menu_state = TripMenuState()
        # self._state_manager = StateManager()
        self._selection_manager = SelectionManager()
        self._web_update_server = WebUpdateServer(
            self._config_manager.config.ap_name,
            self._config_manager.config.ap_ip,
            self._config_manager.config.ap_password,
        )
        self._gui_drawer = GuiDrawer(display, writer)

        self._buttons_press_start_time = None
        self._buttons_press_active = False
        self._last_single_button_time = 0
        self._single_button_cooldown = 150

        self._route_menu_state.load_from_saved_selection()
        self._trip_menu_state.load_from_saved_selection()

        self._routes_for_menu_display_list = []  # Cache for route display list - it optimizes performance

        # temprorary
        self._state = None
        self._current_screen = ScreenStates.STATUS_SCREEN
        self._error_code = ErrorCodes.NONE
        self._message_to_display = None
        self._dirty = True
        self.transition_to(self._state)

    def transition_to(self, state: State):
        self._state = state
        self._state.context = self

    @property
    def current_screen(self):
        return self._current_screen

    @current_screen.setter
    def current_screen(self, value: str):
        self._current_screen = value

    @property
    def max_number_of_characters_in_line(self):
        return self._max_number_of_characters_in_line

    @max_number_of_characters_in_line.setter
    def max_number_of_characters_in_line(self, value: int):
        self._max_number_of_characters_in_line = value

    @property
    def error_code(self):
        return self._error_code

    @error_code.setter
    def error_code(self, value: int):
        self._error_code = value

    @property
    def message_to_display(self):
        return self._message_to_display

    @message_to_display.setter
    def message_to_display(self, value: str | None):
        self._message_to_display = value

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value: bool):
        self._dirty = value

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
        self._dirty = False

    def is_dirty(self):
        return self._dirty

    def draw_current_screen(self):
        if not self.is_dirty():
            return

        current_screen = self.current_screen

        if current_screen == ScreenStates.ROUTE_MENU:
            if len(self._routes_for_menu_display_list) == 0:
                self._routes_for_menu_display_list = self.get_route_list_to_display(
                    self._routes_manager._db_file_path
                )
            highlighted_item_index = self._get_menu_state(
                ScreenStates.ROUTE_MENU
            )._highlighted_item_index
            number_of_menu_items = self.get_number_of_menu_items()

            self._gui_drawer._draw_menu(
                self._routes_for_menu_display_list,
                "Маршрут:",
                highlighted_item_index,
                number_of_menu_items,
            )
        elif current_screen == ScreenStates.TRIP_MENU:
            route = self._routes_manager.get_route_by_index(
                self._route_menu_state.highlighted_item_index
            )
            menu_items = self.get_trip_list_to_display(route)
            highlighted_item_index = self._get_menu_state(
                ScreenStates.TRIP_MENU
            )._highlighted_item_index
            number_of_menu_items = self.get_number_of_menu_items()

            self._gui_drawer._draw_menu(
                menu_items,
                "Напрямок:",
                highlighted_item_index,
                number_of_menu_items,
                f"M:{route['route_number']}",
            )
        elif current_screen == ScreenStates.STATUS_SCREEN:
            self.context.draw_current_screen()
        elif current_screen == ScreenStates.ERROR_SCREEN:
            self._gui_drawer.draw_error_screen(
                str(self.error_code),
                self.message_to_display,
            )

        elif current_screen == ScreenStates.INITIAL_SCREEN:
            self._gui_drawer.draw_initial_screen()
        elif current_screen == ScreenStates.SETTINGS_SCREEN:
            self._gui_drawer.draw_active_settings_screen(self._config_manager.config)
        elif current_screen == ScreenStates.UPDATE_SCREEN:
            self._gui_drawer.draw_update_mode_screen(
                self._config_manager.config.ap_ip, self._config_manager.config.ap_name
            )
        elif current_screen == ScreenStates.MESSAGE_SCREEN:
            self._gui_drawer.draw_message_screen(self.message_to_display)

        self.mark_clean()

    def navigate_up(self, menu_type: str) -> None:
        menu_state = self._get_menu_state(menu_type)
        if menu_state.highlighted_item_index > 0:
            menu_state.highlighted_item_index -= 1

    def navigate_down(self, menu_type: str) -> None:
        menu_state = self._get_menu_state(menu_type)
        get_number_of_menu_items = self.get_number_of_menu_items()

        if menu_state.highlighted_item_index < get_number_of_menu_items - 1:
            menu_state.highlighted_item_index += 1

    def _get_menu_state(self, menu_type: str) -> RouteMenuState | TripMenuState:
        if menu_type == ScreenStates.ROUTE_MENU:
            return self._route_menu_state
        elif menu_type == ScreenStates.TRIP_MENU:
            return self._trip_menu_state
        else:
            set_error_and_raise(
                ErrorCodes.UNKNOWN_MENU_TYPE,
                ValueError(f"Unknown menu type: {menu_type}"),
                True,
            )

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
            True if press duration was long enough to trigger a system state change.
        """
        all_pressed = all(not b for b in buttons_pressed)

        if not all_pressed:
            self._buttons_press_active = False
            self._buttons_press_start_time = None
            return False

        if not self._buttons_press_active:
            self._buttons_press_start_time = current_time
            self._buttons_press_active = True
            return False

        duration = time.ticks_diff(current_time, self._buttons_press_start_time)

        if duration >= 3000:
            if self.current_screen == current_screen:
                self.current_screen = target_screen

                self._buttons_press_active = False
                self._buttons_press_start_time = None
                return True
            else:
                self._buttons_press_active = False
                self._buttons_press_start_time = None

        return False

    def handle_buttons(
        self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int
    ) -> None:
        current_time = time.ticks_ms()

        if not btn_up and not btn_down:
            if self._check_buttons_press_timer(
                [btn_up, btn_down],
                ScreenStates.STATUS_SCREEN,
                ScreenStates.SETTINGS_SCREEN,
                current_time,
            ):
                self.mark_dirty()
                return
            return

        if not btn_down and not btn_select:
            if self.current_screen == ScreenStates.SETTINGS_SCREEN:
                if self._check_buttons_press_timer(
                    [btn_down, btn_select],
                    ScreenStates.SETTINGS_SCREEN,
                    ScreenStates.UPDATE_SCREEN,
                    current_time,
                ):
                    self._web_update_server.ensure_started()
                    self.mark_dirty()
                    return

            elif self.current_screen == ScreenStates.ERROR_SCREEN:
                if self._check_buttons_press_timer(
                    [btn_down, btn_select],
                    ScreenStates.ERROR_SCREEN,
                    ScreenStates.UPDATE_SCREEN,
                    current_time,
                ):
                    self._web_update_server.ensure_started()
                    self.mark_dirty()
                    return

            elif self.current_screen == ScreenStates.INITIAL_SCREEN:
                if self._check_buttons_press_timer(
                    [btn_down, btn_select],
                    ScreenStates.INITIAL_SCREEN,
                    ScreenStates.UPDATE_SCREEN,
                    current_time,
                ):
                    self._web_update_server.ensure_started()
                    self.mark_dirty()
                    return
            return

        if (
            time.ticks_diff(current_time, self._last_single_button_time)
            < self._single_button_cooldown
        ):
            return

        if not btn_menu:
            if self.current_screen == ScreenStates.STATUS_SCREEN:
                self.current_screen = ScreenStates.ROUTE_MENU
                self.mark_dirty()
            elif self.current_screen == ScreenStates.ROUTE_MENU:
                self.current_screen = ScreenStates.STATUS_SCREEN
                self.mark_dirty()
            elif self.current_screen == ScreenStates.TRIP_MENU:
                self.current_screen = ScreenStates.ROUTE_MENU
                self.mark_dirty()
            elif self.current_screen == ScreenStates.SETTINGS_SCREEN:
                self.current_screen = ScreenStates.STATUS_SCREEN
                self.mark_dirty()
            elif self.current_screen == ScreenStates.UPDATE_SCREEN:
                if self.error_code:
                    if self._check_buttons_press_timer(
                        [btn_menu],
                        ScreenStates.UPDATE_SCREEN,
                        ScreenStates.ERROR_SCREEN,
                        current_time,
                    ):
                        self._web_update_server.stop()
                        self.mark_dirty()
                        return
                elif self.current_screen == ScreenStates.INITIAL_SCREEN:
                    if self._check_buttons_press_timer(
                        [btn_menu],
                        ScreenStates.UPDATE_SCREEN,
                        ScreenStates.INITIAL_SCREEN,
                        current_time,
                    ):
                        self._web_update_server.stop()
                        self.mark_dirty()
                        return
                else:
                    if self._check_buttons_press_timer(
                        [btn_menu],
                        ScreenStates.UPDATE_SCREEN,
                        ScreenStates.STATUS_SCREEN,
                        current_time,
                    ):
                        self._web_update_server.stop()
                        self.mark_dirty()
                        return
                return
            self._last_single_button_time = current_time

        if not btn_up:
            if self.current_screen in (
                ScreenStates.ROUTE_MENU,
                ScreenStates.TRIP_MENU,
            ):
                self.navigate_up(self.current_screen)
                self.mark_dirty()
            if self.current_screen == ScreenStates.STATUS_SCREEN:
                self.current_screen = ScreenStates.TRIP_MENU
                self.mark_dirty()
            self._last_single_button_time = current_time

        if not btn_down:
            if self.current_screen in (
                ScreenStates.ROUTE_MENU,
                ScreenStates.TRIP_MENU,
            ):
                self.navigate_down(self.current_screen)
                self.mark_dirty()
            self._last_single_button_time = current_time

        if not btn_select:
            if self.current_screen == ScreenStates.ROUTE_MENU:
                self.current_screen = ScreenStates.TRIP_MENU
                self._trip_menu_state.highlighted_item_index = 0
                self.mark_dirty()
            elif self.current_screen == ScreenStates.TRIP_MENU:
                self._route_menu_state.selected_item_index = (
                    self._route_menu_state.highlighted_item_index
                )
                self._trip_menu_state.selected_item_index = (
                    self._trip_menu_state.highlighted_item_index
                )
                route = self._routes_manager.get_route_by_index(
                    self._route_menu_state.selected_item_index
                )
                self._config_manager.update_current_selection(
                    route["route_number"],
                    route["dirs"][self._trip_menu_state.selected_item_index],
                    route.get("no_line_telegram", False),
                )
                self._selection_manager.save_selection(
                    self._route_menu_state.highlighted_item_index,
                    self._trip_menu_state.highlighted_item_index,
                )
                self.current_screen = ScreenStates.STATUS_SCREEN
                self.mark_dirty()
            elif self.current_screen == ScreenStates.MESSAGE_SCREEN:
                self.current_screen = ScreenStates.STATUS_SCREEN
                self.mark_dirty()

            self._last_single_button_time = current_time

        self._buttons_press_active = False
        self._buttons_press_start_time = None

    def mark_dirty(self):
        self.mark_dirty()

    def is_dirty(self) -> bool:
        return self.is_dirty()

    def mark_clean(self):
        self.mark_clean()

    def get_route_list_to_display(self, route_file_path) -> list[str]:
        routes = self._routes_manager._route_list

        labels = {}

        try:
            with open(route_file_path, "r") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                    except Exception:
                        continue
                    if record.get("t") == "dir":
                        route_id = record.get("rid")
                        if route_id is not None and route_id not in labels:
                            labels[route_id] = record.get("s") or record.get("f", "")
                            if len(labels) == len(routes):
                                break
        except OSError:
            pass

        result = []
        for route_info in routes:
            route_id = route_info["id"]
            route_number = route_info["n"]
            note = route_info.get("note")

            if note:
                result.append(f"{route_number} {note}")
            else:
                name_list = labels.get(route_id, "")
                if not name_list:
                    result.append(route_number)
                elif len(name_list) == 2:
                    result.append(f"{route_number} {name_list[0]} - {name_list[1]}")
                else:
                    result.append(f"{route_number} {name_list[0]}")
        return result

    def get_trip_list_to_display(self, route) -> list[str]:
        menu_items = []
        for d in route.get("dirs", []):
            name_list = d.get("short_name") or d.get("full_name", "")
            if len(name_list) == 2:
                name = name_list[1]
            else:
                name = name_list[0]

            menu_items.append(f"{d.get('trip_id')} {name}")
        return menu_items

    def get_number_of_menu_items(self) -> int:
        if self.current_screen == ScreenStates.ROUTE_MENU:
            return self._routes_manager.get_length_of_routes()
        elif self.current_screen == ScreenStates.TRIP_MENU:
            return self._routes_manager.get_length_of_trips(
                self._route_menu_state.highlighted_item_index
            )
        else:
            return 0
