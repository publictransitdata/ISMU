class ErrorCodes:
    NONE = 0
    # Config errors (1XX)
    # File errors (10X)
    CONFIG_FILE_NOT_FOUND = 100
    CONFIG_IO_ERROR = 101
    TEMP_SELECTION_WRITE_ERROR = 102
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
    ROUTES_FILE_OPEN_FAILED = 202
    ROUTES_FILE_LOAD_ERROR = 203

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
    ROUTE_VALUE_IS_WRONG = 315
    POINT_ID_VALUE_IS_WRONG = 316
    TRIP_NAME_IS_WRONG = 317
    TRIP_NAME_IS_NONE = 318
    TRIP_NAME_OR_ROUTE_NUMBER_IS_WRONG = 319

    # Files errors (4XX)
    # File not found (40X)
    MISSING_LANGUAGE_FILE = 400

    # GUI errors (5XX)
    UNKNOWN_MENU_TYPE = 500

    # Web server errors (6XX)
    WEB_SERVER_SHUTDOWN_ERROR = 600
    WEB_SERVER_ERROR = 601

    # Main loop errors (7XX)
    MAIN_LOOP_ERROR = 700
    GUI_LOOP_ERROR = 701

    MESSAGES = None

    @classmethod
    def _load_messages(cls):
        cls.MESSAGES = {
            # Config
            100: "Файл конфігурації не знайдено",
            101: "Помилка IO конфігурації",
            102: "Помилка запису тим. вибору",
            103: "Перейменуйте config.example на config.txt та заповніть параметри",
            104: "Помилка завантаження конфігурації",
            105: "Файл конфігурації порожній",
            # Config - parse
            110: "Помилка парсування конфігурації",
            111: "Відсутній символ '=' у рядку",
            # Config - validation
            120: "Невідомий ключ конфігурації",
            121: "Невірне значення конфігурації",
            122: "Очікується ціле число",
            123: "Очікується true/false",
            # Routes - file
            200: "Файл маршрутів не знайдено",
            201: "Файл маршрутів порожній",
            202: "Помилка відкриття файлу маршрутів",
            203: "Помилка завантаження маршрутів",
            # Routes - route number
            210: "Порожній номер маршруту",
            211: "Маршрути у файлі відсутні",
            # Routes - direction
            220: "Напрямок без маршруту",
            221: "Порожній ID напрямку або зупинки",
            222: "Неправильна кількість полей",
            # Routes - short name
            230: "Відсутній символ '^' у короткій назві",
            231: "Коротка назва має менше 2 частин",
            # IBIS - codes
            300: "DS001",
            301: "DS001NEU",
            302: "DS003,в номері маршруту лише цифри",
            303: "DS003A",
            # IBIS - data
            310: "Невідомий тип телеграми",
            311: "Номер маршруту відсутній",
            312: "Інформація про рейс відсутня",
            313: "Помилка завантаження таблиці символів. Файл char_map.json має бути у папці config. Дивіться readme.",
            314: "ID зупинки відсутній",
            315: "Невірне значення маршруту",
            316: "Невірне значення ID зупинки",
            317: "Невірна назва рейсу",
            318: "Назва рейсу відсутня",
            319: "Невірна код рейсу/номер маршруту",
            # Files
            400: "Відсутній файл мови. Файл lang.py має бути у папці config. Дивіться readme.",
            # GUI
            500: "Невідомий тип меню",
            # Web server
            600: "Помилка зупинки веб-сервера",
            601: "Помилка веб-сервера",
            # Main loop
            700: "Помилка в головному циклі",
            701: "Помилка в циклі GUI",
        }

    @classmethod
    def get_message(cls, code: int) -> str:
        if cls.MESSAGES is None:
            cls._load_messages()
        return cls.MESSAGES.get(code, f"E{code}: Невідома помилка")
