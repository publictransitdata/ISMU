from app.error_codes import ErrorCodes


def set_error_and_raise(error_code: int, exception=None):
    """
    Sets the error screen with the code and raises an exception.

    Args:
        error_code: code from ErrorCodes
        exception: Optional exception to re-raise
    """
    from app.gui_management import ScreenConfig, ScreenStates

    screen_config = ScreenConfig()
    screen_config.current_screen = ScreenStates.ERROR_SCREEN
    screen_config.error_code = error_code

    if exception:
        raise exception
    raise RuntimeError(ErrorCodes.get_message(error_code))
