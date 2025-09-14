from .singleton_decorator import singleton


class ScreenStates:
    STATUS_SCREEN = "status"
    ROUTE_MENU = "route"
    DIRECTION_MENU = "direction"
    ERROR_SCREEN = "error"
    SETTINGS_SCREEN = "settings"
    UPDATE_SCREEN = "update"


@singleton
class ScreenConfig:
    """
    Attributes:
        _width (int): Width of the screen in pixels.
        _height (int): Height of the screen in pixels.
        _font_size (int): Font size used for rendering text (default: 12).
        _arrow_size (int): Size of navigation arrows (default: 6).
        _max_visible_items_count (int): Maximum number of items visible at once (default: 2).
        _current_screen (str): Identifier of the current active screen.
    """

    def __init__(self):
        self._width = 0
        self._height = 0
        self._font_size = 0
        self._arrow_size = 0
        self._max_visible_items_count = 0
        self._current_screen = None

    def set_screen_config(
        self,
        width: int,
        height: int,
        font_size: int,
        arrow_size: int = 6,
        max_visible_items_count: int = 2,
        current_screen: ScreenStates = ScreenStates.STATUS_SCREEN,
    ):
        self._width = width
        self._height = height
        self._font_size = font_size
        self._arrow_size = arrow_size
        self._max_visible_items_count = max_visible_items_count
        self._current_screen = current_screen

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value: int):
        self._height = value

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
    def max_visible_items_count(self):
        return self._max_visible_items_count

    @max_visible_items_count.setter
    def max_visible_items_count(self, value: int):
        self._max_visible_items_count = value

    @property
    def current_screen(self):
        return self._current_screen

    @current_screen.setter
    def current_screen(self, value: str):
        self._current_screen = value


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
class DirectionMenuState:
    def __init__(self):
        self._selected_item_index = 0
        self._highlighted_item_index = 0

    def set_direction_state(self, direction_selected_item_index: int = 0):
        self._selected_item_index = direction_selected_item_index
        self._highlighted_item_index = direction_selected_item_index

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
