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


@singleton
class RouteMenuData:
    def __init__(self):
        self.selected_item_index = 0
        self.highlighted_item_index = 0

    def load_from_saved_selection(self):
        selection = SelectionManager().get_selection()
        self.selected_item_index = selection["route_id"]
        self.highlighted_item_index = selection["route_id"]


@singleton
class TripMenuData:
    def __init__(self):
        self.selected_item_index = 0
        self.highlighted_item_index = 0

    def set_trip_state(self, trip_selected_item_index: int = 0):
        self.selected_item_index = trip_selected_item_index
        self.highlighted_item_index = trip_selected_item_index

    def load_from_saved_selection(self):
        selection = SelectionManager().get_selection()
        self.selected_item_index = selection["trip_id"]
        self.highlighted_item_index = selection["trip_id"]
