import time

from .state import State


class TripMenuState(State):
    def draw_current_screen(self):
        ctx = self.context
        route = ctx._routes_manager.get_route_by_index(ctx._route_menu_data.highlighted_item_index)
        menu_items = ctx.get_trip_list_to_display(route)
        highlighted_item_index = ctx._get_menu_data(self).highlighted_item_index
        number_of_menu_items = ctx.get_number_of_menu_items()
        ctx._gui_drawer._draw_menu(
            menu_items,
            "Напрямок:",
            highlighted_item_index,
            number_of_menu_items,
            f"M:{route['route_number']}",
        )

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        from .route_menu_state import RouteMenuState
        from .status_state import StatusState

        current_time = time.ticks_ms()
        ctx = self.context

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_menu:
            ctx.transition_to(RouteMenuState())
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
            ctx._route_menu_data.selected_item_index = ctx._route_menu_data.highlighted_item_index
            ctx._trip_menu_data.selected_item_index = ctx._trip_menu_data.highlighted_item_index
            ctx._selection_manager.update_selection(
                ctx._route_menu_data.highlighted_item_index,
                ctx._trip_menu_data.highlighted_item_index,
            )
            ctx.transition_to(StatusState())
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return
