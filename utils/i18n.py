try:
    from config.lang import strings as _current_strings  # type: ignore
except ImportError:
    from app.error_codes import ErrorCodes
    from utils.error_handler import set_error_and_raise

    set_error_and_raise(ErrorCodes.MISSING_LANGUAGE_FILE)
    _current_strings = {}


def string(key):
    return _current_strings.get(key, key)
