class CustomError(Exception):
    def __init__(self, error_code: int, detail: str = ""):
        self.error_code = error_code
        self.detail = detail
        super().__init__(detail)
