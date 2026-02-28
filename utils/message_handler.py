def set_message(message: str):
    """
    Sets the message screen with the info for usere, user can switch to another state from this state.

    Args:
        message: text to display on the message screen
    """
    from app.gui_management import ScreenConfig, ScreenStates

    screen_config = ScreenConfig()
    screen_config.current_screen = ScreenStates.MESSAGE_SCREEN
    screen_config.mark_dirty()
    screen_config.message_to_display = message
