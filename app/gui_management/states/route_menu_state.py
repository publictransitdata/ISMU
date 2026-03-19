import time

from .state import State


class RouteMenuState(State):
    def draw_current_screen(self):
        ctx = self.context
        if len(ctx._routes_for_menu_display_list) == 0:
            ctx._routes_for_menu_display_list = ctx.get_route_list_to_display(
                ctx._routes_manager._db_file_path
            )
        highlighted_item_index = ctx._get_menu_data(self).highlighted_item_index
        number_of_menu_items = ctx.get_number_of_menu_items()

        ctx._gui_drawer._draw_menu(
            ctx._routes_for_menu_display_list,
            "Маршрут:",
            highlighted_item_index,
            number_of_menu_items,
        )

    def handle_buttons(
        self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int
    ):
        from .status_state import StatusState
        from .trip_menu_state import TripMenuState
        current_time = time.ticks_ms()
        ctx = self.context

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_menu:
            ctx.transition_to(StatusState())
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return

        if not btn_up:
            ctx.navigate_up(self)
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return

        if not btn_down:
            ctx.navigate_down(self)
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return

        if not btn_select:
            ctx.transition_to(TripMenuState())
            ctx._trip_menu_data.highlighted_item_index = 0
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return
