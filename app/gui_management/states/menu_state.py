import time

from .state import State


class MenuState(State):
    title = ""
    menu_items = ()

    def __init__(self):
        self.highlighted_item_index = 0

    def draw_current_screen(self):
        ctx = self.context
        ctx._gui_drawer._draw_menu(
            self.menu_items,
            self.title,
            self.highlighted_item_index,
            len(self.menu_items),
        )

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        current_time = time.ticks_ms()
        ctx = self.context

        if ctx._is_in_cooldown(current_time):
            return

        if not btn_menu:
            self.go_back()
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return

        if not btn_up:
            if self.highlighted_item_index > 0:
                self.highlighted_item_index -= 1
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return

        if not btn_down:
            if self.highlighted_item_index < len(self.menu_items) - 1:
                self.highlighted_item_index += 1
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time
            return

        if not btn_select:
            self.select_item(self.highlighted_item_index)
            ctx.mark_dirty()
            ctx._last_single_button_time = current_time

    def go_back(self) -> None:
        raise NotImplementedError("go_back method should be implemented in the subclass")

    def select_item(self, index: int) -> None:
        """Nothing to open by default - info screens are read-only."""
