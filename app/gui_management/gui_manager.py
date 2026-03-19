import sys
import time

import ujson as json

from app.config_management import ConfigManager
from app.error_codes import ErrorCodes
from app.routes_management import RoutesManager
from app.selection_management import SelectionManager
from app.web_update import WebUpdateServer
from utils.error_handler import set_error_and_raise
from utils.gui_hooks import (
    register_error_hook,
    register_initial_hook,
    register_message_hook,
)

from .gui_config import (
    RouteMenuData,
    TripMenuData,
)
from .gui_drawer import GuiDrawer
from .states import (
    ErrorState,
    InitialState,
    MessageState,
    RouteMenuState,
    State,
    StatusState,
    TripMenuState,
)

if sys.platform != "rp2":
    from lib.sh1106 import SH1106_I2C  # for vs code
    from lib.writer import Writer  # for vs code


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
        self._web_update_server = WebUpdateServer(
            self._config_manager.config.ap_name,
            self._config_manager.config.ap_ip,
            self._config_manager.config.ap_password,
        )
        self._route_menu_data = RouteMenuData()
        self._trip_menu_data = TripMenuData()
        self._selection_manager = SelectionManager()
        self._gui_drawer = GuiDrawer(display, writer)

        self._buttons_press_start_time = None
        self._buttons_press_active = False
        self._last_single_button_time = 0
        self._single_button_cooldown = 150

        self._route_menu_data.load_from_saved_selection()
        self._trip_menu_data.load_from_saved_selection()

        self._routes_for_menu_display_list = []  # Cache for route display list - it optimizes performance

        self._state = StatusState()
        self._error_code = ErrorCodes.NONE
        self._message_to_display = None
        self._dirty = True
        self.transition_to(self._state)

        register_error_hook(self._handle_error)
        register_message_hook(self._handle_message)
        register_initial_hook(self._handle_initial)

    def transition_to(self, state: State):
        self._state = state
        self._state.context = self

    def _handle_error(self, error_code: int, message: str | None):
        self._error_code = error_code
        self._message_to_display = message
        self.transition_to(ErrorState())
        self.mark_dirty()

    def _handle_message(self, message: str, error_code: int | None):
        self._error_code = error_code if error_code is not None else ErrorCodes.NONE
        self._message_to_display = message
        self.transition_to(MessageState())
        self.mark_dirty()

    def _handle_initial(self):
        self.transition_to(InitialState())
        self.mark_dirty()

    @property
    def error_code(self):
        return self._error_code

    @error_code.setter
    def error_code(self, value: int):
        self.transition_to(ErrorState())
        self._error_code = value
        self.mark_dirty()

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
        self._dirty = False

    def is_dirty(self):
        return self._dirty

    def draw_current_screen(self):
        if not self.is_dirty():
            return

        self._state.draw_current_screen()
        self.mark_clean()

    def navigate_up(self, menu_type: RouteMenuState | TripMenuState) -> None:
        menu_state = self._get_menu_data(menu_type)
        if menu_state.highlighted_item_index > 0:
            menu_state.highlighted_item_index -= 1

    def navigate_down(self, menu_type: RouteMenuState | TripMenuState) -> None:
        menu_state = self._get_menu_data(menu_type)
        get_number_of_menu_items = self.get_number_of_menu_items()

        if menu_state.highlighted_item_index < get_number_of_menu_items - 1:
            menu_state.highlighted_item_index += 1

    def _get_menu_data(self, menu_type: RouteMenuState | TripMenuState) -> RouteMenuData | TripMenuData:
        if isinstance(menu_type, RouteMenuState):
            return self._route_menu_data
        elif isinstance(menu_type, TripMenuState):
            return self._trip_menu_data
        else:
            set_error_and_raise(
                ErrorCodes.UNKNOWN_MENU_TYPE,
                ValueError(f"Unknown menu type: {menu_type}"),
                show_message=True,
            )

    def get_number_of_menu_items(self) -> int:
        if isinstance(self._state, RouteMenuState):
            return self._routes_manager.get_length_of_routes()
        elif isinstance(self._state, TripMenuState):
            return self._routes_manager.get_length_of_trips(self._route_menu_data.highlighted_item_index)
        else:
            return 0

    def _is_in_cooldown(self, current_time) -> bool:
        return time.ticks_diff(current_time, self._last_single_button_time) < self._single_button_cooldown

    def _is_long_pressed(
        self,
        buttons_pressed: list[int],
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
            self._buttons_press_active = False
            self._buttons_press_start_time = None
            return True

        return False

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int) -> None:
        self._state.handle_buttons(btn_menu, btn_up, btn_down, btn_select)

    def get_route_list_to_display(self, route_file_path) -> list[str]:
        routes = self._routes_manager._route_list

        labels = {}

        try:
            with open(route_file_path) as f:
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
