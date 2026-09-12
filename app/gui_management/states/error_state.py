import time

from .state import State


class ErrorState(State):
    def draw_current_screen(self):
        ctx = self.context
        ctx._gui_drawer.draw_error_screen(
            str(ctx.error_code),
            ctx._message_to_display,
        )

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        from .update_state import UpdateState

        current_time = time.ticks_ms()
        ctx = self.context

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_select:
            ctx.enter_web_update()
            ctx.transition_to(UpdateState(ErrorState()))
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
