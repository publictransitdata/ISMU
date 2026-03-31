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

    # GUI errors (5XX)
    UNKNOWN_MENU_TYPE = 500

    # Web server errors (6XX)
    WEB_SERVER_SHUTDOWN_ERROR = 600
    WEB_SERVER_ERROR = 601

    # Main loop errors (7XX)
    MAIN_LOOP_ERROR = 700

    MESSAGES = None

    @classmethod
    def _load_messages(cls):
        cls.MESSAGES = {
            # Config
            100: "Файл конфігурації не знайдено",
            101: "Помилка запису тим. вибору",
            102: "Перейменуйте config.example на config.json та заповніть параметри",
            103: "Помилка перевірки файлу конфігурації",
            104: "Помилка завантаження JSON з файлу конфігурації",
            105: "Помилка відкриття файлу конфігурації",
            # Routes - file
            200: "Файл маршрутів не знайдено",
            201: "Файл маршрутів порожній",
            202: "Помилка відкриття файлу маршрутів",
            203: "Помилка перевірки файлу маршрутів",
            # IBIS - data
            300: "Невідомий тип телеграми",
            301: "Номер маршруту відсутній",
            302: "Інформація про рейс відсутня",
            303: "Помилка завантаження таблиці символів. Файл char_map.json має бути у папці config. Дивіться readme.",
            304: "ID зупинки відсутній",
            305: "Невірне значення маршруту",
            306: "Невірне значення ID зупинки",
            307: "Невірна назва рейсу",
            308: "Назва рейсу відсутня",
            309: "Невірна код рейсу/номер маршруту",
            # Files
            400: "Відсутній файл мови. Файл lang.py має бути у папці config. Дивіться readme.",
            # GUI
            500: "Невідомий тип меню",
            # Web server
            600: "Помилка зупинки веб-сервера",
            601: "Помилка веб-сервера",
            # Main loop
            700: "Помилка в головному циклі",
        }

    @classmethod
    def get_message(cls, code: int) -> str:
        if cls.MESSAGES is None:
            cls._load_messages()
        return cls.MESSAGES.get(code, f"E{code}: Невідома помилка")
