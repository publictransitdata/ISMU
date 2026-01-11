from utils.singleton_decorator import singleton


class ScreenStates:
    STATUS_SCREEN = "status"
    ROUTE_MENU = "route"
    TRIP_MENU = "trip"
    ERROR_SCREEN = "error"
    SETTINGS_SCREEN = "settings"
    UPDATE_SCREEN = "update"
    INITIAL_SCREEN = "initial"
    START_SCREEN = "start"


@singleton
class ScreenConfig:
    """
    Attributes:
        _screen_width (int): in pixels.
        _screen_height (int): in pixels.
        _font_size (int): Font size used for rendering text.
        _max_menu_items (int): Maximum number of items visible at once on screen.
        _current_screen (str): Identifier of the current active screen.
        _error_code (int): Error code to display on error screen.
    """

    def __init__(self):
        self._screen_width = 0
        self._screen_height = 0
        self._font_size = 0
        self._arrow_size = 0
        self._max_menu_items = 0
        self._max_number_of_characters_in_line = 0
        self._current_screen = ScreenStates.STATUS_SCREEN
        self._is_system_fresh = False
        self._error_code = 0

    def set_screen_config(
        self,
        screen_width: int,
        screen_height: int,
        font_size: int,
        arrow_size: int = 6,
        max_menu_items: int = 2,
        max_number_of_characters_in_line: int = 18,
    ):
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._font_size = font_size
        self._arrow_size = arrow_size
        self._max_menu_items = max_menu_items
        self._max_number_of_characters_in_line = max_number_of_characters_in_line

    @property
    def screen_width(self):
        return self._screen_width

    @screen_width.setter
    def screen_width(self, value: int):
        self._screen_width = value

    @property
    def screen_height(self):
        return self._screen_height

    @screen_height.setter
    def screen_height(self, value: int):
        self._screen_height = value

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value: int):
        self._font_size = value

    @property
    def arrow_size(self):
        return self._arrow_size

    @arrow_size.setter
    def arrow_size(self, value: int):
        self._arrow_size = value

    @property
    def max_menu_items(self):
        return self._max_menu_items

    @max_menu_items.setter
    def max_menu_items(self, value: int):
        self._max_menu_items = value

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
    def is_system_fresh(self):
        return self._is_system_fresh

    @is_system_fresh.setter
    def is_system_fresh(self, value: bool):
        self._is_system_fresh = value


@singleton
class RouteMenuState:
    def __init__(self):
        self._selected_item_index = 0
        self._highlighted_item_index = 0

    @property
    def selected_item_index(self):
        return self._selected_item_index

    @selected_item_index.setter
    def selected_item_index(self, value):
        self._selected_item_index = value

    @property
    def highlighted_item_index(self):
        return self._highlighted_item_index

    @highlighted_item_index.setter
    def highlighted_item_index(self, value):
        self._highlighted_item_index = value


@singleton
class TripMenuState:
    def __init__(self):
        self._selected_item_index = 0
        self._highlighted_item_index = 0

    def set_trip_state(self, trip_selected_item_index: int = 0):
        self._selected_item_index = trip_selected_item_index
        self._highlighted_item_index = trip_selected_item_index

    @property
    def selected_item_index(self):
        return self._selected_item_index

    @selected_item_index.setter
    def selected_item_index(self, value):
        self._selected_item_index = value

    @property
    def highlighted_item_index(self):
        return self._highlighted_item_index

    @highlighted_item_index.setter
    def highlighted_item_index(self, value):
        self._highlighted_item_index = value
