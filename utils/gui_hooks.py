_on_error = None
_on_message = None
_on_initial = None


def register_error_hook(callback):
    global _on_error
    _on_error = callback


def register_message_hook(callback):
    global _on_message
    _on_message = callback


def register_initial_hook(callback):
    global _on_initial
    _on_initial = callback


def trigger_error(error_code, message=None):
    if _on_error:
        _on_error(error_code, message)


def trigger_message(message: str, error_code=None):
    if _on_message:
        _on_message(message, error_code)


def trigger_initial():
    if _on_initial:
        _on_initial()
