class ErrorCodes:
    NONE = 0
    # Config errors (1XX)
    CONFIG_FILE_NOT_FOUND = 100
    TEMP_SELECTION_WRITE_ERROR = 101
    CONFIG_EXAMPLE_EXIST = 102
    CONFIG_CHECKER_FAILED = 103
    CONFIG_JSON_LOAD_ERROR = 104
    CONFIG_FILE_OPEN_FAILED = 105

    # Routes errors (2XX)
    ROUTES_FILE_NOT_FOUND = 200
    ROUTES_FILE_EMPTY = 201
    ROUTES_FILE_OPEN_FAILED = 202
    ROUTES_CHECKER_FAILED = 203

    # IBIS errors (3XX)
    UNKNOWN_TELEGRAM = 300
    ROUTE_NUMBER_IS_NONE = 301
    TRIP_INFO_IS_NONE = 302
    CHAR_MAP_LOAD_ERROR = 303
    POINT_ID_IS_NONE = 304
    ROUTE_VALUE_IS_WRONG = 305
    POINT_ID_VALUE_IS_WRONG = 306
    TRIP_NAME_IS_WRONG = 307
    TRIP_NAME_IS_NONE = 308
    TRIP_NAME_OR_ROUTE_NUMBER_IS_WRONG = 309

    # Files errors (4XX)
    MISSING_LANGUAGE_FILE = 400
    MISSING_FONT_FILE = 401

    # GUI errors (5XX)
    UNKNOWN_MENU_TYPE = 500

    # Web server errors (6XX)
    WEB_SERVER_SHUTDOWN_ERROR = 600
    WEB_SERVER_ERROR = 601

    # Main loop errors (7XX)
    MAIN_LOOP_ERROR = 700
    GUI_LOOP_ERROR = 701

    @classmethod
    def get_message(cls, code: int) -> str:
        from utils.i18n import string

        return string(f"E{code}")
