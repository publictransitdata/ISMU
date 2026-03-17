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
        writer: Writer,
    ):
        """
        Initializes the GuiDrawer with the necessary configurations and display components.

        Args:
            display: The display object used for rendering content on the screen.
            writers: The writer objects used for rendering string_line on the screen.
        """
        self._display = display
        self._writer = writer
        self._screen_config = ScreenConfig()

    def _draw_menu(
        self,
        menu_items: list[str],
        header_text: str,
        highlighted_item_index: int,
        number_of_menu_items: int,
        header_suffix: str = "",
    ) -> None:
        """
        Draws a menu on the display. There is same template for route and trip menus.

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
        bottom_offset = self._screen_config.screen_height - 1
        top_offset_with_up_arrow = top_offset + self._screen_config.arrow_size + 2
        screen_center_width = int(self._screen_config.screen_width / 2)
        max_menu_items = self._screen_config.max_menu_items

        self._display.fill(0)

        self._writer.set_textpos(self._display, 0, left_offset)
        self._writer.printstring(header_text, False)

        if header_suffix:
            header_text_width = self._writer.stringlen(header_text)
            separator_x = left_offset + header_text_width + 7  # 7px offset

            suffix_x = separator_x + 3  # 3px offset
            self._writer.set_textpos(self._display, 0, suffix_x)
            self._writer.printstring(header_suffix, False)

            self._display.vline(separator_x, 0, line_height + 2, 1)

            self._display.fill_rect(
                separator_x, line_height + 1, self._screen_config.screen_width, 1, 1
            )

        first_visible_menu_item_idx = (
            highlighted_item_index // max_menu_items
        ) * max_menu_items
        last_visible_menu_item_idx = min(
            first_visible_menu_item_idx + max_menu_items,
            len(menu_items),
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

    def trim_text_to_fit(
        self, string_line: str, max_number_of_characters_in_line: int = 18
    ) -> str:
        return string_line[0:max_number_of_characters_in_line]

    def draw_status_screen(
        self,
        selected_trip_name: str,
        selected_route_id: str,
        selected_trip_id: int,
        selected_trip_number: int,
    ) -> None:
        line_height = self._screen_config.font_size + 2
        left_offset = 2
        screen_height = self._screen_config.screen_height

        self._display.fill(0)

        self._writer.set_textpos(self._display, 0, left_offset)
        self._writer.printstring("> " + selected_trip_name, False)

        bottom_y = screen_height - line_height
        self._writer.set_textpos(self._display, bottom_y, left_offset)
        self._writer.printstring(
            f"М:{selected_route_id}",
            False,
        )

        route_text_width = self._writer.stringlen(f"М:{selected_route_id}")
        trip_text_width = self._writer.stringlen(f"Н:{selected_trip_id:02d}")

        self._writer.set_textpos(
            self._display, bottom_y, left_offset + route_text_width + 3
        )

        self._writer.printstring(
            f"Н:{selected_trip_id:02d}",
            False,
        )

        self._writer.set_textpos(
            self._display,
            bottom_y,
            left_offset + route_text_width + trip_text_width + 6,
        )

        self._writer.printstring(
            f"К:{selected_trip_number}",
            False,
        )

        self._display.show()

    def draw_error_screen(self, error_code: str, message: str | None = None) -> None:
        self._display.fill(0)

        if not message:
            line_height = self._screen_config.font_size + 2
            screen_width = self._screen_config.screen_width
            screen_height = self._screen_config.screen_height

            line1 = f"Помилка: {error_code}"

            centrized_top_y = (screen_height - line_height) // 2

            line1_width = self._writer.stringlen(line1)
            line1_offset = (screen_width - line1_width) // 2

            self._writer.set_textpos(self._display, centrized_top_y, line1_offset)
            self._writer.printstring(line1, False)

        else:
            line_height = self._screen_config.font_size + 2
            screen_width = self._screen_config.screen_width

            line1 = f"Помилка: {error_code}"

            line_height = self._screen_config.font_size + 2
            line1_width = self._writer.stringlen(line1)
            line1_offset = (screen_width - line1_width) // 2

            self._writer.set_textpos(self._display, 0, line1_offset)
            self._writer.printstring(line1, False)

            self._writer.set_textpos(self._display, line_height + 2, 0)
            self._writer.printstring(message, False)

        self._display.show()

    def draw_message_screen(self, message: str | None) -> None:
        self._display.fill(0)

        line_height = self._screen_config.font_size + 2
        screen_width = self._screen_config.screen_width
        screen_height = self._screen_config.screen_height

        bottom_y = screen_height - line_height

        note_for_user = ">Натисни OK<"

        message_width = self._writer.stringlen(note_for_user)
        message_offset = (screen_width - message_width) // 2

        self._writer.set_textpos(self._display, 0, 0)
        self._writer.printstring(message, False)

        self._writer.set_textpos(self._display, bottom_y, message_offset)
        self._writer.printstring(note_for_user, False)

        self._display.show()

    def draw_initial_screen(self) -> None:
        self._display.fill(0)
        self._writer.set_textpos(self._display, 0, 0)
        self._writer.printstring(
            "Потрібно завантажити файли конфігурації та маршрутів", False
        )
        self._display.show()

    def draw_update_mode_screen(self, ip_address: str, ap_name: str) -> None:
        self._display.fill(0)

        line_height = self._screen_config.font_size + 2
        screen_width = self._screen_config.screen_width
        screen_height = self._screen_config.screen_height

        line1 = "Режим оновлення"
        line2 = f"{ap_name}"
        line3 = f"ІР:{ip_address}"

        total_height = line_height * 3
        top_y = (screen_height - total_height) // 2

        line1_width = self._writer.stringlen(line1)
        line2_width = self._writer.stringlen(line2)
        line3_width = self._writer.stringlen(line3)

        line1_offset = (screen_width - line1_width) // 2
        line2_offset = (screen_width - line2_width) // 2
        line3_offset = (screen_width - line3_width) // 2

        self._writer.set_textpos(self._display, top_y, line1_offset)
        self._writer.printstring(line1, False)

        self._writer.set_textpos(self._display, top_y + line_height + 2, line2_offset)
        self._writer.printstring(line2, False)

        self._writer.set_textpos(
            self._display, top_y + line_height * 2 + 2, line3_offset
        )
        self._writer.printstring(line3, False)

        self._display.show()

    def draw_active_settings_screen(self, config) -> None:
        line_height = self._screen_config.font_size + 2
        left_offset = 2
        screen_height = self._screen_config.screen_height

        self._display.fill(0)

        self._writer.set_textpos(self._display, 0, 0)

        telegrams_list = [
            config.line_telegram,
            config.destination_number_telegram,
            config.destination_telegram,
            config.stop_board_telegram,
        ]
        filtered_telegrams = [t for t in telegrams_list if t]
        telegrams_text = ", ".join(filtered_telegrams)

        self._writer.printstring(
            f"Telegrams: {telegrams_text}",
            False,
        )

        bottom_y = screen_height - line_height
        self._writer.set_textpos(self._display, bottom_y, left_offset)
        self._writer.printstring(f"ver:{config.version}", False)

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
            available_width = self._screen_config.max_number_of_characters_in_line
            string_line = self.trim_text_to_fit(menu_items[i], available_width)

            if is_highlighted:
                self._display.fill_rect(
                    0, y, self._screen_config.screen_width, line_height, 1
                )
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(string_line, True)
            else:
                self._writer.set_textpos(self._display, y, left_offset)
                self._writer.printstring(string_line, False)

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
                is_arrow_trip_up=True,
            )

        if last_visible_menu_item_idx < number_of_menu_items:
            self.draw_arrow(
                arrow_center_x,
                down_arrow_tip_y,
                self._screen_config.arrow_size,
                is_arrow_trip_up=False,
            )

    def draw_arrow(
        self,
        arrow_center_x: int,
        arrow_tip_y: int,
        arrow_height: int,
        is_arrow_trip_up: bool,
    ) -> None:
        coef = 1 if is_arrow_trip_up else -1
        for i in range(arrow_height):
            for j in range(-i * 2, (i * 2) + 1):
                self._display.pixel(arrow_center_x + j, arrow_tip_y + i * coef, 1)
