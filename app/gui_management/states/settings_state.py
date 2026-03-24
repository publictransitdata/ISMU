import time

from .state import State


class SettingsState(State):
    def draw_current_screen(self):
        ctx = self.context
        ctx._gui_drawer.draw_active_settings_screen(ctx._config_manager.config)

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        from .status_state import StatusState
        from .update_state import UpdateState

        current_time = time.ticks_ms()
        ctx = self.context

        if not btn_down and not btn_select:
            if ctx._is_long_pressed(
                [btn_down, btn_select],
                current_time,
            ):
                ctx._web_update_server.ensure_started()
                ctx.transition_to(UpdateState(StatusState()))
                ctx.mark_dirty()
                return
            return

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_menu:
            ctx.transition_to(StatusState())
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return
