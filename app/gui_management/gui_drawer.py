import sys

from .gui_config import (
    ScreenConfig,
)

if sys.platform != "rp2":
    from lib.sh1106 import SH1106_I2C  # for vs code
    from lib.writer import Writer  # for vs code


class GuiDrawer:
    def __init__(
        self,
        display: SH1106_I2C,
        writers: list[Writer],
        screen_config: ScreenConfig,
    ):
        self._display = display
        self._writers = writers
        self._screen_config = screen_config

    def _draw_menu(
        self,
        menu_items: list[str],
        header_text: str,
        highlighted_item_index: int,
        number_of_menu_items: int,
        header_suffix: str = "",
    ) -> None:
        """
        Draws a menu on the display. There is same template for route and direction menus.

        Args:
            menu_items: A list of menu items to display.
            header_text: The text to display in the menu header.
            highlighted_item_index: The index of the currently highlighted menu item.
            number_of_menu_items:
            header_suffix: Additional text to display in the header.
        """
        line_height = self._screen_config.font_size + 2
        top_offset = line_height + 3  # 3 = line and two pixel spacing on the sides
        left_offset = 2
        bottom_offset = self._screen_config.height - 1
        top_offset_with_up_arrow = top_offset + self._screen_config.arrow_size + 2
        screen_center_width = int(self._screen_config.width / 2)
        max_visible_items_count = self._screen_config.max_visible_items_count

        self._display.fill(0)

        self._writers[0].set_textpos(self._display, 0, left_offset)
        self._writers[0].printstring(f"{header_text}{header_suffix}", False)
        self._display.fill_rect(0, line_height + 1, self._screen_config.width, 1, 1)

        first_visible_menu_item_idx = (
            highlighted_item_index // max_visible_items_count
        ) * max_visible_items_count
        last_visible_menu_item_idx = min(
            first_visible_menu_item_idx + max_visible_items_count, len(menu_items)
        )

        self.draw_menu_items(
            menu_items,
            first_visible_menu_item_idx,
            last_visible_menu_item_idx,
            line_height,
            top_offset_with_up_arrow,
            left_offset,
            highlighted_item_index,
        )

        self.draw_arrows(
            screen_center_width,
            top_offset,
            bottom_offset,
            first_visible_menu_item_idx,
            last_visible_menu_item_idx,
            number_of_menu_items,
        )

        self._display.show()

    def trim_text_to_fit(self, string_line: str, max_width_of_line: int) -> str:
        if self._writers[0].stringlen(string_line) <= max_width_of_line:
            return string_line

        for i in range(len(string_line), 0, -1):
            trimmed = string_line[:i]
            if self._writers[0].stringlen(trimmed) <= max_width_of_line:
                return trimmed

        return "..."

    def draw_status_screen(
        self,
        selected_direction_name: str,
        selected_route_id: str,
        selected_direction_id: int,
        selected_direction_number: int,
    ) -> None:
        line_height = self._screen_config.font_size + 2
        left_offset = 2
        screen_height = self._screen_config.height

        self._display.fill(0)

        self._writers[0].set_textpos(self._display, 0, left_offset)
        self._writers[0].printstring("> " + selected_direction_name, False)

        bottom_y = screen_height - line_height
        self._writers[0].set_textpos(self._display, bottom_y, left_offset)
        self._writers[0].printstring(
            f"М:{selected_route_id}Н:{selected_direction_id:02d}К:{selected_direction_number}",
            False,
        )

        self._display.show()

    def draw_error_screen(self, error_message: str) -> None:
        self._display.fill(0)
        self._writers[0].set_textpos(self._display, 0, 0)
        self._writers[0].printstring(error_message, False)
        self._display.show()

    def draw_update_mode_screen(self, ip_address: str, ap_name: str) -> None:
        self._display.fill(0)

        line_height = self._screen_config.font_size + 2
        screen_width = self._screen_config.width
        screen_height = self._screen_config.height

        line1 = "Режим оновлення"
        line2 = f"{ap_name}"
        line3 = f"ІР:{ip_address}"

        top_y = int((screen_height - line_height * 2) / 2)

        line1_width = self._writers[0].stringlen(line1)
        line2_width = self._writers[1].stringlen(line2)
        line3_width = self._writers[0].stringlen(line3)

        line1_offset = (screen_width - line1_width) // 2
        line2_offset = (screen_width - line2_width) // 2
        line3_offset = (screen_width - line3_width) // 2

        self._writers[0].set_textpos(self._display, top_y, line1_offset)
        self._writers[0].printstring(line1, False)

        self._writers[1].set_textpos(
            self._display, top_y + line_height + 2, line2_offset
        )
        self._writers[1].printstring(line2, False)

        self._writers[0].set_textpos(
            self._display, top_y + line_height * 2 + 2, line3_offset
        )
        self._writers[0].printstring(line3, False)

        self._display.show()

    def draw_active_settings_screen(self, config) -> None:
        line_height = self._screen_config.font_size + 2
        left_offset = 2
        screen_height = self._screen_config.height

        self._display.fill(0)

        self._writers[1].set_textpos(self._display, 0, 0)

        self._writers[1].printstring(
            f"Telegrams: {config.line}, {config.destination_number}, {config.destination}, {config.stop_display_telegram}",
            False,
        )

        bottom_y = screen_height - line_height
        self._writers[1].set_textpos(self._display, bottom_y, left_offset)
        self._writers[1].printstring(f"ver:{config.version}", False)

        self._display.show()

    def draw_menu_items(
        self,
        menu_items: list[str],
        first_visible_menu_item_idx: int,
        last_visible_menu_item_idx: int,
        line_height: int,
        top_offset: int,
        left_offset: int,
        highlighted_item_index,
    ) -> None:
        for i in range(first_visible_menu_item_idx, last_visible_menu_item_idx):
            y = top_offset + (i - first_visible_menu_item_idx) * line_height
            is_highlighted = i == highlighted_item_index
            available_width = self._screen_config.width - left_offset
            string_line = self.trim_text_to_fit(menu_items[i], available_width)

            if is_highlighted:
                self._display.fill_rect(0, y, self._screen_config.width, line_height, 1)
                self._writers[0].set_textpos(self._display, y, left_offset)
                self._writers[0].printstring(string_line, True)
            else:
                self._writers[0].set_textpos(self._display, y, left_offset)
                self._writers[0].printstring(string_line, False)

    def draw_arrows(
        self,
        arrow_center_x: int,
        up_arrow_tip_y: int,
        down_arrow_tip_y: int,
        first_visible_menu_item_idx: int,
        last_visible_menu_item_idx: int,
        number_of_menu_items: int,
    ) -> None:
        if first_visible_menu_item_idx > 0:
            self.draw_arrow(
                arrow_center_x,
                up_arrow_tip_y,
                self._screen_config.arrow_size,
                is_arrow_direction_up=True,
            )

        if last_visible_menu_item_idx < number_of_menu_items:
            self.draw_arrow(
                arrow_center_x,
                down_arrow_tip_y,
                self._screen_config.arrow_size,
                is_arrow_direction_up=False,
            )

    def draw_arrow(
        self,
        arrow_center_x: int,
        arrow_tip_y: int,
        arrow_height: int,
        is_arrow_direction_up: bool,
    ) -> None:
        coef = 1 if is_arrow_direction_up else -1
        for i in range(arrow_height):
            for j in range(-i * 2, (i * 2) + 1):
                self._display.pixel(arrow_center_x + j, arrow_tip_y + i * coef, 1)
