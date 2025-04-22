class ScreenConfig:
    def __init__(self, width: int, height: int, font_size: int):
        self.width = width
        self.height = height
        self.font_size = font_size


class MenuConfig:
    def __init__(self, arrow_size: int = 6, visible_items: int = 2, selected: int = 0):
        self.arrow_size = arrow_size
        self.visible_items = visible_items
        self.selected = selected
