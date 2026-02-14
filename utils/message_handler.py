def set_message(message: str):
    from app.gui_management import ScreenConfig, ScreenStates

    screen_config = ScreenConfig()
    screen_config.current_screen = ScreenStates.MESSAGE_SCREEN
    screen_config.mark_dirty()
    screen_config.message_to_display = message
