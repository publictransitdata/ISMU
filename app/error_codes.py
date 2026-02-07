class ErrorCodes:
    # Config errors (1XX)
    # File errors (10X)
    CONFIG_FILE_NOT_FOUND = 100
    CONFIG_IO_ERROR = 101
    TEMP_STATE_WRITE_ERROR = 102

    # Parse errors (11X)
    CONFIG_PARSE_ERROR = 110
    CONFIG_NO_EQUALS_SIGN = 111

    # Validation errors (12X)
    CONFIG_UNKNOWN_KEY = 120
    CONFIG_INVALID_VALUE = 121

    # Routes errors (2XX)
    # File errors (20X)
    ROUTES_FILE_NOT_FOUND = 200
    ROUTES_FILE_EMPTY = 201
    ROUTES_DB_OPEN_FAILED = 202
    ROUTES_DB_WRITE_FAILED = 203

    # Route number errors (21X)
    ROUTES_EMPTY_ROUTE_NUMBER = 210
    ROUTES_NO_ROUTES_FOUND = 211

    # Direction errors (22X)
    ROUTES_DIRECTION_WITHOUT_ROUTE = 220
    ROUTES_DIRECTION_EMPTY_ID = 221
    ROUTES_DIRECTION_WRONG_PARTS_COUNT = 222

    # Short name errors (23X)
    ROUTES_SHORT_NAME_NO_SEPARATOR = 230
    ROUTES_SHORT_NAME_TOO_FEW_PARTS = 231

    MESSAGES = {
        # Config
        100: "E100: Config not found",
        101: "E101: Config IO error",
        102: "E102: Temp state write error",
        # Config - parse
        110: "E110: Config parse fail",
        111: "E111: Missing '=' in line",
        # Config - validation
        120: "E120: Unknown config key",
        121: "E121: Invalid config val",
        122: "E122: Expected integer",
        123: "E123: Expected true/false",
        # Routes - file
        200: "E200: Routes not found",
        201: "E201: Routes file empty",
        202: "E202: Routes DB open fail",
        203: "E203: Routes DB write fail",
        # Routes - route number
        210: "E210: Empty route number",
        211: "E211: No routes in file",
        # Routes - direction
        220: "E220: Dir without route",
        222: "E221: Empty dir/point ID",
        223: "E222: Wrong field count",
        # Routes - short name
        230: "E230: Short name no '^'",
        231: "E231: Short name <2 parts",
    }

    @classmethod
    def get_message(cls, code: int) -> str:
        return cls.MESSAGES.get(code, f"E{code}: Unknown error")
