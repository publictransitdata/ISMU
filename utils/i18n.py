try:
    from lang import strings as _current_strings  # type: ignore
except ImportError:
    from app.error_codes import ErrorCodes
    from utils.error_handler import set_error_and_raise

    set_error_and_raise(ErrorCodes.MISSING_LANGUAGE_FILE)
    _current_strings = {}

_menu_strings = None


def string(key):
    value = _current_strings.get(key)
    if value is not None:
        return value
    return _menu_screen_strings().get(key, key)


def _menu_screen_strings():
    global _menu_strings

    if _menu_strings is None:
        try:
            import lang_menu  # type: ignore

            _menu_strings = lang_menu.strings
        except ImportError:
            from app.error_codes import ErrorCodes
            from utils.error_handler import set_error_and_raise

            set_error_and_raise(ErrorCodes.MISSING_LANGUAGE_FILE, raise_exception=False)
            _menu_strings = {}
    return _menu_strings
