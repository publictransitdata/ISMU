from utils.i18n import string

from .menu_state import MenuState


class MainMenuState(MenuState):
    title = string("gui_title_main_menu")
    menu_items = (
        string("gui_item_system_status"),
        string("gui_item_update_mode"),
    )

    def go_back(self):
        from .nav_menu_state import NavMenuState

        self.context.transition_to(NavMenuState())

    def select_item(self, index: int):
        from .system_status_menu_state import SystemStatusMenuState
        from .update_state import UpdateState

        ctx = self.context

        if index == 0:
            ctx.transition_to(SystemStatusMenuState())
        elif index == 1:
            ctx.enter_web_update()
            ctx.transition_to(UpdateState(MainMenuState()))
