from .singleton_decorator import singleton


class ScreenStates:
    STATUS_SCREEN = "status"
    ROUTE_MENU = "route"
    DIRECTION_MENU = "direction"
    ERROR_SCREEN = "error"


@singleton
class ScreenConfig:
    def __init__(self):
        self._width = 0
        self._height = 0
        self._font_size = 0
        self._arrow_size = 0
        self._visible_items = 0
        self._current_screen = None

    def set_screen_config(
        self,
        width: int,
        height: int,
        font_size: int,
        arrow_size: int = 6,
        visible_items: int = 2,
        current_screen: str = ScreenStates.STATUS_SCREEN,
    ):
        self._width = width
        self._height = height
        self._font_size = font_size
        self._arrow_size = arrow_size
        self._visible_items = visible_items
        self._current_screen = ScreenStates.STATUS_SCREEN

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
    def visible_items(self):
        return self._visible_items

    @visible_items.setter
    def visible_items(self, value: int):
        self._visible_items = value

    @property
    def current_screen(self):
        return self._current_screen

    @current_screen.setter
    def current_screen(self, value: str):
        self._current_screen = value


@singleton
class RouteMenuState:
    def __init__(self):
        self._number_of_options = 0
        self._selected = 0

    def set_route_state(self, route_length: int, route_selected: int = 0):
        self._number_of_options = route_length
        self._selected = route_selected

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value

    @property
    def number_of_options(self):
        return self._number_of_options

    @number_of_options.setter
    def number_of_options(self, value):
        self._number_of_options = value


@singleton
class DirectionMenuState:
    def __init__(self):
        self._number_of_options = 0
        self._selected = 0

    def set_direction_state(self, direction_length: int, direction_selected: int = 0):
        self._number_of_options = direction_length
        self._selected = direction_selected

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value

    @property
    def number_of_options(self):
        return self._number_of_options

    @number_of_options.setter
    def number_of_options(self, value):
        self._number_of_options = value
