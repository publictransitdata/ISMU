import os

import ujson as json

ALLOWED_ROUTES_CHARS = set(
    " []{}!\"'+,-./0123456789:<=>?ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_abcdefghijklmnopqrstuvwxyz()"
    "ÓóĄąĆćĘęŁłŚśŻżЄІЇАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзийклмнопрстуфхцчшщьюяєії^#|\n\r,+"
)

ALLOWED_CONFIG_CHARS = set(
    "\t\n\r !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
)


VALID_CONFIG_KEYS = {
    "line_telegram",
    "destination_number_telegram",
    "destination_telegram",
    "show_start_and_end_stops",
    "force_short_names",
    "stop_board_telegram",
    "show_info_on_stop_board",
    "ap_name",
    "ap_password",
    "ap_ip",
    "baudrate",
    "bits",
    "parity",
    "stop",
}


def check_invalid_chars_file(filepath: str, allowed_chars: set) -> list:
    errors = []
    line_num = 1
    char_index = 0
    try:
        with open(filepath) as f:
            while True:
                chunk = f.read(128)
                if not chunk:
                    break
                for ch in chunk:
                    if ch == "\n":
                        line_num += 1
                    elif ch == "\r":
                        pass
                    elif ch not in allowed_chars:
                        errors.append(f"Рядок {line_num}: Недопустимий символ '{ch}'")
                        if len(errors) >= 5:
                            errors.append("... (ще є помилки)")
                            return errors
                    char_index += 1
    except UnicodeDecodeError as err:
        return [f"Невірне кодування файлу (позиція {err.start})"]
    return errors


def file_is_empty(filepath: str) -> bool:
    try:
        s = os.stat(filepath)
        if s[6] == 0:
            return True
    except OSError:
        return True
    with open(filepath) as f:
        while True:
            chunk = f.read(128)
            if not chunk:
                return True
            if chunk.strip():
                return False


def _find_duplicate_key(s):
    seen = set()
    i = 0
    n = len(s)
    depth = 0
    while i < n:
        ch = s[i]
        if ch == '"':
            i += 1
            s_start = i
            while i < n:
                if s[i] == "\\":
                    i += 2
                    continue
                if s[i] == '"':
                    break
                i += 1
            key = s[s_start:i]
            i += 1
            if depth == 1:
                j = i
                while j < n and s[j] in " \t\n\r":
                    j += 1
                if j < n and s[j] == ":":
                    if key in seen:
                        return key
                    seen.add(key)
        elif ch == "{":
            depth += 1
            i += 1
        elif ch == "}":
            depth -= 1
            i += 1
        else:
            i += 1
    return None


def _check_config_json_structure(s):
    i = 0
    n = len(s)

    while i < n and s[i] in " \t\n\r":
        i += 1
    if i >= n or s[i] != "{":
        return None
    i += 1

    while i < n and s[i] in " \t\n\r":
        i += 1
    if i < n and s[i] == "}":
        return None

    while True:
        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n or s[i] == "}":
            return None

        if s[i] != '"':
            return "Очікувався ключ у лапках у файлі налаштувань"
        i += 1
        key_start = i
        while i < n:
            if s[i] == "\\":
                i += 2
                continue
            if s[i] == '"':
                break
            i += 1
        key = s[key_start:i]
        i += 1

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n or s[i] != ":":
            return f"Відсутнє ':' після ключа '{key}'"
        i += 1

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n:
            return f"Відсутнє значення для ключа '{key}'"
        ch = s[i]
        if ch == '"':
            i += 1
            while i < n:
                if s[i] == "\\":
                    i += 2
                    continue
                if s[i] == '"':
                    i += 1
                    break
                i += 1
        elif ch in "-0123456789":
            while i < n and s[i] in "-0123456789.eE+":
                i += 1
        elif s[i : i + 4] == "true":
            i += 4
        elif s[i : i + 5] == "false":
            i += 5
        elif s[i : i + 4] == "null":
            i += 4
        else:
            return f"Невідоме значення для ключа '{key}'"

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n:
            return None
        if s[i] == ",":
            i += 1
        elif s[i] == "}":
            return None
        else:
            return "Відсутня кома між парами ключ:значення"


def _check_routes_ndjson_line_structure(s):
    i = 0
    n = len(s)

    while i < n and s[i] in " \t\n\r":
        i += 1
    if i >= n or s[i] != "{":
        return None
    i += 1

    while i < n and s[i] in " \t\n\r":
        i += 1
    if i < n and s[i] == "}":
        return None

    while True:
        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n or s[i] == "}":
            return None

        if s[i] != '"':
            return "Очікувався ключ у лапках"
        i += 1
        key_start = i
        while i < n:
            if s[i] == "\\":
                i += 2
                continue
            if s[i] == '"':
                break
            i += 1
        key = s[key_start:i]
        i += 1

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n or s[i] != ":":
            return f"Відсутнє ':' після ключа '{key}'"
        i += 1

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n:
            return f"Відсутнє значення для ключа '{key}'"
        ch = s[i]
        if ch == '"':
            i += 1
            while i < n:
                if s[i] == "\\":
                    i += 2
                    continue
                if s[i] == '"':
                    i += 1
                    break
                i += 1
        elif ch in "-0123456789":
            while i < n and s[i] in "-0123456789.eE+":
                i += 1
        elif s[i : i + 4] == "true":
            i += 4
        elif s[i : i + 5] == "false":
            i += 5
        elif s[i : i + 4] == "null":
            i += 4
        elif ch == "[":
            i += 1
            while i < n and s[i] in " \t\n\r":
                i += 1
            if i < n and s[i] == "]":
                i += 1
            else:
                while True:
                    while i < n and s[i] in " \t\n\r":
                        i += 1
                    if i >= n or s[i] != '"':
                        return f"Очікувався рядок у списку для ключа '{key}'"
                    i += 1
                    while i < n:
                        if s[i] == "\\":
                            i += 2
                            continue
                        if s[i] == '"':
                            i += 1
                            break
                        i += 1
                    while i < n and s[i] in " \t\n\r":
                        i += 1
                    if i >= n:
                        return f"Незакритий список для ключа '{key}'"
                    if s[i] == ",":
                        i += 1
                    elif s[i] == "]":
                        i += 1
                        break
                    else:
                        return f"Відсутня кома у списку для ключа '{key}'"
        else:
            return f"Невідоме значення для ключа '{key}'"

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n:
            return None
        if s[i] == ",":
            i += 1
        elif s[i] == "}":
            return None
        else:
            return "Відсутня кома між парами ключ:значення"


def check_config_content_file(filepath: str) -> list:
    errors = []

    if file_is_empty(filepath):
        return ["Файл налаштувань порожній"]

    char_errors = check_invalid_chars_file(filepath, ALLOWED_CONFIG_CHARS)
    if char_errors:
        return char_errors

    try:
        with open(filepath) as f:
            content = f.read()
    except OSError:
        return ["Помилка відкриття файлу налаштувань"]

    dup = _find_duplicate_key(content)
    if dup is not None:
        errors.append(f"Дублікат ключа '{dup}'")
        return errors

    struct_err = _check_config_json_structure(content)
    if struct_err is not None:
        return [struct_err]

    try:
        cfg = json.loads(content)
    except Exception:
        return ["Файл налаштувань містить невірний JSON"]

    if not isinstance(cfg, dict):
        return ["Файл налаштувань не є об'єктом JSON"]

    unknown = set(cfg) - VALID_CONFIG_KEYS
    if unknown:
        errors.append(f"Невідомі параметри: {', '.join(sorted(unknown))}")

    missing = VALID_CONFIG_KEYS - set(cfg)
    if missing:
        errors.append(f"Відсутні обов'язкові параметри: {', '.join(sorted(missing))}")

    if errors:
        return errors

    nullable_keys = {"line_telegram", "destination_number_telegram", "destination_telegram", "stop_board_telegram"}
    str_keys = {"ap_name", "ap_password", "ap_ip"}
    bool_keys = {"show_start_and_end_stops", "force_short_names", "show_info_on_stop_board"}
    int_keys = {"baudrate", "bits", "parity", "stop"}

    for key in nullable_keys:
        v = cfg[key]
        if v is not None and not isinstance(v, str):
            errors.append(f"Параметр '{key}' має бути рядком або пустим")

    for key in str_keys:
        v = cfg[key]
        if not isinstance(v, str):
            errors.append(f"Параметр '{key}' має бути рядком")
        elif not v:
            errors.append(f"Параметр '{key}' не може бути порожнім")

    for key in bool_keys:
        v = cfg[key]
        if not isinstance(v, bool):
            errors.append(f"Параметр '{key}' має бути true або false")

    for key in int_keys:
        v = cfg[key]
        if isinstance(v, bool) or not isinstance(v, int):
            errors.append(f"Параметр '{key}' має бути цілим числом")

    return errors


def check_routes_content_file(filepath: str) -> list:
    errors = []

    if file_is_empty(filepath):
        return ["Файл маршрутів порожній"]

    char_errors = check_invalid_chars_file(filepath, ALLOWED_ROUTES_CHARS)
    if char_errors:
        return char_errors

    current_route_id = None
    current_route_has_dirs = False
    current_route_line = None
    line_num = 0
    seen_route_ids = set()
    seen_p_ids = set()

    def _check_type(value, expected_type: type, field: str):
        if value is None:
            return
        if not isinstance(value, expected_type):
            errors.append(f"Рядок {line_num}: Поле '{field}' має неправильні дані")

    def _require_field(rec, field: str):
        if field not in rec:
            errors.append(f"Рядок {line_num}: Відсутній '{field}'")
            return None
        return rec[field]

    def _check_list_of_str(value, field: str):
        if value is None:
            return
        if not isinstance(value, list):
            errors.append(f"Рядок {line_num}: Поле '{field}' має бути списком")
            return
        for item in value:
            if not isinstance(item, str):
                errors.append(f"Рядок {line_num}: Поле '{field}' має містити лише рядки")
                return

    try:
        with open(filepath) as f:
            for line in f:
                line_num += 1
                struct_err = _check_routes_ndjson_line_structure(line)
                if struct_err is not None:
                    errors.append(f"Рядок {line_num}: {struct_err}")
                    if len(errors) >= 10:
                        errors.append("... (ще є помилки)")
                        break
                    continue

                try:
                    rec = json.loads(line)
                except Exception:
                    errors.append(f"Рядок {line_num}: Невірний JSON")

                for key in rec:
                    if line.count('"' + key + '":') > 1:
                        errors.append(f"Рядок {line_num}: Дублікат ключа '{key}'")
                        break

                if "id" in rec and "did" in rec:
                    errors.append(f"Рядок {line_num}: Запис містить одночасно 'id' та 'did'")
                    break
                elif "id" not in rec and "did" not in rec:
                    errors.append(f"Рядок {line_num}: Невідомий тип запису (немає 'id' або 'did')")
                    break

                if "id" in rec:
                    unknown = set(rec) - {"id", "r", "nlt", "note"}
                    if unknown:
                        errors.append(f"Рядок {line_num}: Невідомі поля: {', '.join(sorted(unknown))}")
                    if current_route_id is not None and not current_route_has_dirs:
                        errors.append(f"Рядок {current_route_line}: Маршрут не має жодного напрямку")
                    _check_type(rec["id"], int, "id")
                    _check_type(_require_field(rec, "r"), str, "r")
                    if "nlt" in rec:
                        _check_type(rec["nlt"], bool, "nlt")
                    if "note" in rec:
                        _check_type(rec["note"], str, "note")
                    if rec["id"] in seen_route_ids:
                        errors.append(f"Рядок {line_num}: Дублікат id маршруту '{rec['id']}'")
                    else:
                        seen_route_ids.add(rec["id"])
                    current_route_id = rec["id"]
                    current_route_has_dirs = False
                    current_route_line = line_num

                if "did" in rec:
                    unknown = set(rec) - {"did", "p", "f", "s"}
                    if unknown:
                        errors.append(f"Рядок {line_num}: Невідомі поля: {', '.join(sorted(unknown))}")
                    _check_type(rec["did"], int, "did")

                    _check_type(_require_field(rec, "p"), int, "p")

                    _check_list_of_str(_require_field(rec, "f"), "f")
                    if "s" in rec:
                        _check_list_of_str(rec["s"], "s")

                    if "p" in rec:
                        if rec["p"] in seen_p_ids:
                            errors.append(f"Рядок {line_num}: Дублікат індексу напрямку '{rec['p']}'")
                        else:
                            seen_p_ids.add(rec["p"])

                    if current_route_id is None:
                        errors.append(f"Рядок {line_num}: Напрямок без заголовку маршруту")
                    elif current_route_id != rec["did"]:
                        errors.append(
                            f"Рядок {line_num}: Напрямок не належить маршруту над ним "
                            f"(очікується did={current_route_id})"
                        )
                        if len(errors) >= 10:
                            errors.append("... (ще є помилки)")
                            break

                    current_route_has_dirs = True

                if len(errors) >= 10:
                    errors.append("... (ще є помилки)")
                    break
    except OSError:
        return ["Помилка відкриття файлу маршрутів"]

    return errors
