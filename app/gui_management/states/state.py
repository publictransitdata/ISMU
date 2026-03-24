class State:
    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    def handle_buttons(self, btn_menu: int, btn_up: int, btn_down: int, btn_select: int):
        raise NotImplementedError("handle_buttons method should be implemented in the subclass")

    def draw_current_screen(self):
        raise NotImplementedError("draw_current_screen method should be implemented in the subclass")
