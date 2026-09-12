import time

from .state import State


class StatusState(State):
    def draw_current_screen(self):
        ctx = self.context
        route = ctx._routes_manager.get_route_by_index(ctx._route_menu_data.selected_item_index)
        selected_trip_name_list = route["dirs"][ctx._trip_menu_data.selected_item_index]["full_name"]
        if len(selected_trip_name_list) == 2:
            selected_trip_name = selected_trip_name_list[1]
        else:
            selected_trip_name = selected_trip_name_list[0]
        ctx._gui_drawer.draw_status_screen(
            selected_trip_name,
            route["route_number"],
            ctx._trip_menu_data.selected_item_index + 1,
            route["dirs"][ctx._trip_menu_data.selected_item_index]["point_id"],
        )

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        from .nav_menu_state import NavMenuState

        current_time = time.ticks_ms()
        ctx = self.context

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_menu:
            ctx.transition_to(NavMenuState())
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
