import time

from .state import State


class UpdateState(State):
    def __init__(self, return_state=None):
        self._return_state = return_state

    def draw_current_screen(self):
        ctx = self.context
        ctx._gui_drawer.draw_update_mode_screen(ctx._config_manager.config.ap_ip, ctx._config_manager.config.ap_name)

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        from .status_state import StatusState

        current_time = time.ticks_ms()
        ctx = self.context

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_menu:
            if ctx._is_long_pressed(
                [btn_menu],
                current_time,
            ):
                ctx._web_update_server.stop()
                ctx.transition_to(self._return_state or StatusState())
                ctx.mark_dirty()
                ctx._last_single_button_time = current_time
                return

            return
