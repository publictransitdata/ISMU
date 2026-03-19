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
            int(route["dirs"][ctx._trip_menu_data.selected_item_index]["point_id"]),
        )

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        from .route_menu_state import RouteMenuState
        from .settings_state import SettingsState
        from .trip_menu_state import TripMenuState

        current_time = time.ticks_ms()
        ctx = self.context

        if not btn_up and not btn_down:
            if ctx._is_long_pressed(
                [btn_up, btn_down],
                current_time,
            ):
                ctx.transition_to(SettingsState())
                ctx.mark_dirty()
                return
            return

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_menu:
            ctx.transition_to(RouteMenuState())
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return

        if not btn_up:
            ctx.transition_to(TripMenuState())
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return
