import time

from .state import State


class InitialState(State):
    def draw_current_screen(self):
        ctx = self.context
        ctx._gui_drawer.draw_initial_screen()

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        from .update_state import UpdateState

        current_time = time.ticks_ms()
        ctx = self.context

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_select:
            ctx.get_web_update_server().ensure_started()
            ctx.transition_to(UpdateState(InitialState()))
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
