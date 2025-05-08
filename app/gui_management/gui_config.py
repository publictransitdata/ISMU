class ScreenConfig:
    def __init__(
        self,
        width: int,
        height: int,
        font_size: int,
        arrow_size: int = 6,
        visible_items: int = 2,
    ):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.arrow_size = arrow_size
        self.visible_items = visible_items


class RouteMenuConfig:
    def __init__(self, route_length, route_selected: int = 0):
        self.number_of_options = route_length
        self.selected = route_selected


class DirectionMenuConfig:
    def __init__(self, direction_length, direction_selected: int = 0):
        self.number_of_options = direction_length
        self.selected = direction_selected


class MenuStates:
    MAIN_MENU = "main_menu"
    ROUTE_MENU = "route"
    DIRECTION = "direction"
