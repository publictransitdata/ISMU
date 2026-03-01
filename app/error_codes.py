class ErrorCodes:
    # Config errors (1XX)
    # File errors (10X)
    CONFIG_FILE_NOT_FOUND = 100
    CONFIG_IO_ERROR = 101
    TEMP_STATE_WRITE_ERROR = 102
    CONFIG_EXAMPLE_EXIST = 103
    CONFIG_FILE_LOAD_ERROR = 104
    CONFIG_FILE_EMPTY = 105

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
    ROUTES_FILE_OPEN_FAILED = 204
    ROUTES_FILE_LOAD_ERROR = 205

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

    # IBIS errors (3XX)
    # Code errors (30X)
    DS001_ERROR = 300
    DS001NEU_ERROR = 301
    DS003_ERROR = 302
    DS003A_ERROR = 303
    # Data errors (31X)
    UNKNOWN_TELEGRAM = 310
    ROUTE_NUMBER_IS_NONE = 311
    TRIP_INFO_IS_NONE = 312
    CHAR_MAP_LOAD_ERROR = 313
    POINT_ID_IS_NONE = 314

    # Files errors (4XX)
    # File not found (40X)
    MISSING_LANGUAGE_FILE = 400

    # GUI errors (5XX)
    UNKNOWN_MENU_TYPE = 500

    # Web server errors (6XX)
    WEB_SERVER_SHUTDOWN_ERROR = 600
    WEB_SERVER_ERROR = 601
    REFRESH_ROUTES_DB_ERROR = 602

    MESSAGES = {
        # Config
        100: "E100: Config not found",
        101: "E101: Config IO error",
        102: "E102: Temp state write error",
        103: "E103: Rename config.example to config.txt and fill keys to start",
        104: "E104: Config file load error",
        105: "E105: Config file empty",
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
        204: "E204: Routes file open fail",
        205: "E205: Routes file load error",
        # Routes - route number
        210: "E210: Empty route number",
        211: "E211: No routes in file",
        # Routes - direction
        220: "E220: Dir without route",
        221: "E221: Empty dir/point ID",
        222: "E222: Wrong field count",
        # Routes - short name
        230: "E230: Short name no '^'",
        231: "E231: Short name <2 parts",
        # IBIS - codes
        300: "E300: DS001 error",
        301: "E301: DS001NEU error",
        302: "E302: DS003 error, routes numbers should have only numbers(no letters or symbols)",
        303: "E303: DS003A error",
        # IBIS - data
        310: "E310: Unknown telegram type",
        311: "E311: Route number is None",
        312: "E312: Trip info is None",
        313: "E313: Char map load error",
        314: "E314: Point ID is None",
        # Files
        400: "E400: Missing language file",
        # GUI
        500: "E500: Unknown menu type",
        # Web server
        600: "E600: Web server shutdown error",
        601: "E601: Web server error",
        602: "E602: Refresh routes DB error",
    }

    @classmethod
    def get_message(cls, code: int) -> str:
        return cls.MESSAGES.get(code, f"E{code}: Unknown error")
