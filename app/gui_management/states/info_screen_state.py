from .menu_state import MenuState


class InfoScreenState(MenuState):
    def __init__(self, title: str, items: list[str], back_state_class):
        super().__init__()
        self.title = title
        self.menu_items = items
        self._back_state_class = back_state_class

    def go_back(self):
        self.context.transition_to(self._back_state_class())
