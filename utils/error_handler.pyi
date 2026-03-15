from typing import Literal, NoReturn, overload

@overload
def set_error_and_raise(
    error_code: int,
    exception: BaseException | None = ...,
    show_message: bool = ...,
    raise_exception: Literal[True] = ...,
) -> NoReturn: ...
@overload
def set_error_and_raise(
    error_code: int,
    exception: BaseException | None = ...,
    show_message: bool = ...,
    raise_exception: Literal[False] = ...,
) -> None: ...
