

class GuiManager:
    def __init__(self, display, writer):
        self._display = display
        self._writer = writer

    def draw_route_menu(self, routeMenu, selected=0):
        self._display.fill(0)
        self._writer.set_textpos(self._display, 0, 2)
        self._writer.printstring("Маршрут:", 0)
        self._display.fill_rect(0, 14, 128, 1, 1)
        for i, item in enumerate(routeMenu):
            if i == selected:
                self._display.fill_rect(0, (i * 15) + 15, 128, 15, 1)
                self._writer.set_textpos(self._display, (i * 15) + 15, 2)
                self._writer.printstring(item, 1)
            else:
                self._writer.set_textpos(self._display, (i * 15) + 15, 2)
                self._writer.printstring(item, 0)

        self._display.show()