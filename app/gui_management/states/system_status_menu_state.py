from utils.i18n import string

from .menu_state import MenuState


class SystemStatusMenuState(MenuState):
    title = string("gui_title_system_status")
    menu_items = (
        string("gui_item_general_config"),
        string("gui_item_ibis"),
        string("gui_item_network"),
        string("gui_item_about"),
    )

    def go_back(self):
        from .main_menu_state import MainMenuState

        self.context.transition_to(MainMenuState())

    def select_item(self, index: int):
        from .info_screen_state import InfoScreenState

        ctx = self.context
        config = ctx._config_manager.config

        if index == 0:
            title = string("gui_title_general_config")
            items = _general_config_lines(config)
        elif index == 1:
            title = string("gui_title_ibis")
            items = _ibis_lines(config)
        elif index == 2:
            title = string("gui_title_network")
            items = _network_lines(config)
        elif index == 3:
            title = string("gui_title_about")
            items = _about_lines(ctx, config)
        else:
            return

        ctx.transition_to(InfoScreenState(title, items, SystemStatusMenuState))


def _yes_no(value: bool) -> str:
    return string("gui_lbl_yes") if value else string("gui_lbl_no")


def _general_config_lines(config) -> list[str]:
    return [
        string("gui_lbl_start_end_stops").format(_yes_no(config.show_start_and_end_stops)),
        string("gui_lbl_short_names").format(_yes_no(config.force_short_names)),
        string("gui_lbl_board_info").format(_yes_no(config.show_info_on_stop_board)),
        string("gui_lbl_char_map").format(_yes_no(config.use_char_map)),
    ]


def _ibis_lines(config) -> list[str]:
    not_set = string("gui_lbl_not_set")
    return [
        string("gui_lbl_tlg_line").format(config.line_telegram or not_set),
        string("gui_lbl_tlg_dest_number").format(config.destination_number_telegram or not_set),
        string("gui_lbl_tlg_dest").format(config.destination_telegram or not_set),
        string("gui_lbl_tlg_board").format(config.stop_board_telegram or not_set),
        string("gui_lbl_baudrate").format(config.baudrate),
        string("gui_lbl_frame").format(config.bits, config.parity, config.stop),
    ]


def _network_lines(config) -> list[str]:
    return [
        string("gui_lbl_ap_name").format(config.ap_name),
        string("gui_lbl_ap_ip").format(config.ap_ip),
    ]


def _about_lines(ctx, config) -> list[str]:
    route = ctx._routes_manager.get_route_by_index(ctx._route_menu_data.selected_item_index)
    return [
        string("gui_lbl_version").format(config.version),
        string("gui_lbl_routes_count").format(ctx._routes_manager.get_length_of_routes()),
        string("gui_lbl_current_route").format(route["route_number"]),
        string("gui_lbl_current_trip").format(ctx._trip_menu_data.selected_item_index + 1),
    ]
