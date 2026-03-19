import time

from app.error_codes import ErrorCodes

from .state import State


class MessageState(State):
    def draw_current_screen(self):
        ctx = self.context
        error_code = ctx.error_code if ctx.error_code != ErrorCodes.NONE else None
        ctx._gui_drawer.draw_message_screen(ctx._message_to_display, error_code)

    def handle_buttons(
        self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int
    ):
        from .status_state import StatusState
        current_time = time.ticks_ms()
        ctx = self.context

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_select:
            ctx.transition_to(StatusState())
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return