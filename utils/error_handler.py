from app.error_codes import ErrorCodes
from utils.gui_hooks import trigger_error


def set_error_and_raise(
    error_code: int, exception=None, show_message=False, raise_exception=True
):
    """
    Sets the error screen with the code and raises an exception.

    Args:
        error_code: code from ErrorCodes
        exception: Optional exception to re-raise
    """
    message = str(exception) if show_message and exception else None
    trigger_error(error_code, message)

    if not raise_exception:
        return

    if exception:
        raise exception
    raise RuntimeError(ErrorCodes.get_message(error_code))
