from utils.i18n import string

from .menu_state import MenuState


class NavMenuState(MenuState):
    title = string("gui_title_menu")
    menu_items = (
        string("gui_item_direction"),
        string("gui_item_route"),
        string("gui_item_main_menu"),
    )

    def go_back(self):
        from .status_state import StatusState

        self.context.transition_to(StatusState())

    def select_item(self, index: int):
        from .main_menu_state import MainMenuState
        from .route_menu_state import RouteMenuState
        from .trip_menu_state import TripMenuState

        ctx = self.context

        if index == 0:
            self._highlight_current_route()
            self._highlight_current_trip()
            ctx.transition_to(TripMenuState(NavMenuState))
        elif index == 1:
            self._highlight_current_route()
            ctx.transition_to(RouteMenuState())
        elif index == 2:
            ctx.transition_to(MainMenuState())

    def _highlight_current_route(self):
        menu_data = self.context._route_menu_data
        menu_data.highlighted_item_index = menu_data.selected_item_index

    def _highlight_current_trip(self):
        menu_data = self.context._trip_menu_data
        menu_data.highlighted_item_index = menu_data.selected_item_index
