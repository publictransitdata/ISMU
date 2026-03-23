from app.selection_management import SelectionManager
from utils.singleton_decorator import singleton


@singleton
class ScreenConfig:
    """
    Attributes:
        screen_width (int): in pixels.
        screen_height (int): in pixels.
        font_size (int): Font size used for rendering text.
        arrow_size (int): Size of the arrow used for navigation.
        max_menu_items (int): Maximum number of items visible at once on screens of menu(route/trip).
    """

    def __init__(self):
        self.screen_width = 0
        self.screen_height = 0
        self.font_size = 0
        self.arrow_size = 0
        self.max_menu_items = 0
        self.max_number_of_characters_in_line = 0

    def set_screen_config(
        self,
        screen_width: int,
        screen_height: int,
        font_size: int,
        arrow_size: int = 6,
        max_menu_items: int = 2,
        max_number_of_characters_in_line: int = 18,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_size = font_size
        self.arrow_size = arrow_size
        self.max_menu_items = max_menu_items
        self.max_number_of_characters_in_line = max_number_of_characters_in_line


class MenuData:
    def __init__(self, selection_key: str):
        self._selection_key = selection_key
        self._selected_item_index: int | None = None
        self._highlighted_item_index: int | None = None

    def _load_from_selection(self) -> int:
        selection = SelectionManager().get_selection_ids()
        return selection[self._selection_key]

    @property
    def selected_item_index(self) -> int:
        if self._selected_item_index is None:
            value = self._load_from_selection()
            self._selected_item_index = value
            self._highlighted_item_index = value
        return self._selected_item_index

    @selected_item_index.setter
    def selected_item_index(self, value: int):
        self._selected_item_index = value

    @property
    def highlighted_item_index(self) -> int:
        if self._highlighted_item_index is None:
            value = self._load_from_selection()
            self._selected_item_index = value
            self._highlighted_item_index = value
        return self._highlighted_item_index

    @highlighted_item_index.setter
    def highlighted_item_index(self, value: int):
        self._highlighted_item_index = value


@singleton
class RouteMenuData(MenuData):
    def __init__(self):
        super().__init__(selection_key="route_id")


@singleton
class TripMenuData(MenuData):
    def __init__(self):
        super().__init__(selection_key="trip_id")
