from app.selection_management import SelectionManager
from utils.singleton_decorator import singleton


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
    def max_number_of_characters_in_line(self):
        return self._max_number_of_characters_in_line

    @max_number_of_characters_in_line.setter
    def max_number_of_characters_in_line(self, value: int):
        self._max_number_of_characters_in_line = value


@singleton
class RouteMenuData:
    def __init__(self):
        self._selected_item_index = 0
        self._highlighted_item_index = 0

    def load_from_saved_selection(self):
        selection = SelectionManager().get_selection()
        self._selected_item_index = selection["route_id"]
        self._highlighted_item_index = selection["route_id"]

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
class TripMenuData:
    def __init__(self):
        self._selected_item_index = 0
        self._highlighted_item_index = 0

    def set_trip_state(self, trip_selected_item_index: int = 0):
        self._selected_item_index = trip_selected_item_index
        self._highlighted_item_index = trip_selected_item_index

    def load_from_saved_selection(self):
        selection = SelectionManager().get_selection()
        self._selected_item_index = selection["trip_id"]
        self._highlighted_item_index = selection["trip_id"]

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
