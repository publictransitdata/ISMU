import os

import ujson as json

from utils.i18n import string

ALLOWED_ROUTES_CHARS = set(
    " []{}!\"'+,-./0123456789:<=>?ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_abcdefghijklmnopqrstuvwxyz()"
    "ÓóĄąĆćĘęŁłŚśŻżЄІЇАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзийклмнопрстуфхцчшщьюяєії^#|\n\r,+"
)

ALLOWED_CONFIG_CHARS = set(
    "\t\n\r !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
)


REQUIRED_CONFIG_KEYS = {
    "line_telegram",
    "destination_number_telegram",
    "destination_telegram",
    "show_start_and_end_stops",
    "force_short_names",
    "stop_board_telegram",
    "show_info_on_stop_board",
    "use_char_map",
    "ap_name",
    "ap_password",
    "ap_ip",
    "baudrate",
    "bits",
    "parity",
    "stop",
}

OPTIONAL_CONFIG_KEYS = {
    "nlt_data",
    "displays",
}

ADDRESSED_TEXT_TELEGRAMS = ("DS021", "DS021neu")
DISPLAY_KEYS = {"addr", "display_type", "enabled", "show_start_and_end_stops", "mode", "width", "font"}
DISPLAY_TYPES = ("external", "internal")
DISPLAY_MODES = ("fixed", "line_feed", "flowing")
DISPLAY_WIDTHS = (16, 24)
MAX_DISPLAY_ADDR = 15


def _check_invalid_chars_file(filepath: str, allowed_chars: set) -> list:
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
                        errors.append(string("fc_invalid_char").format(line_num=line_num, ch=ch))
                        if len(errors) >= 5:
                            errors.append(string("fc_more_errors"))
                            return errors
                    char_index += 1
    except UnicodeDecodeError as err:
        return [string("fc_invalid_encoding").format(err.start)]
    return errors


def _file_is_empty(filepath: str) -> bool:
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
    keys_per_object = []
    i = 0
    n = len(s)
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
            j = i
            while j < n and s[j] in " \t\n\r":
                j += 1
            if keys_per_object and j < n and s[j] == ":":
                if key in keys_per_object[-1]:
                    return key
                keys_per_object[-1].add(key)
        elif ch == "{":
            keys_per_object.append(set())
            i += 1
        elif ch == "}":
            if keys_per_object:
                keys_per_object.pop()
            i += 1
        else:
            i += 1
    return None


def _skip_nested_value(s, i):
    depth = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == '"':
            i += 1
            while i < n and s[i] != '"':
                i += 2 if s[i] == "\\" else 1
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                return i + 1
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
            return string("fc_expected_key_in_config")
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
            return string("fc_missing_colon_after_key").format(key)
        i += 1

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n:
            return string("fc_missing_value_for_key").format(key)
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
        elif ch in "[{":
            i = _skip_nested_value(s, i)
            if i is None:
                return string("fc_config_invalid_json")
        else:
            return string("fc_unknown_value_for_key").format(key)

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n:
            return None
        if s[i] == ",":
            i += 1
        elif s[i] == "}":
            return None
        else:
            return string("fc_missing_comma")


def _check_routes_ndjson_line_structure(s):
    i = 0
    n = len(s)

    while i < n and s[i] in " \t\n\r":
        i += 1
    if i >= n:
        return None
    if s[i] != "{":
        return string("fc_expected_json_object")
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
            return string("fc_expected_key_in_quotes")
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
            return string("fc_missing_colon_after_key").format(key)
        i += 1

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n:
            return string("fc_missing_value_for_key").format(key)
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
                        return string("fc_expected_string_in_list").format(key)
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
                        return string("fc_unclosed_list").format(key)
                    if s[i] == ",":
                        i += 1
                    elif s[i] == "]":
                        i += 1
                        break
                    else:
                        return string("fc_missing_comma_in_list").format(key)
        else:
            return string("fc_unknown_value_for_key").format(key)

        while i < n and s[i] in " \t\n\r":
            i += 1
        if i >= n:
            return None
        if s[i] == ",":
            i += 1
        elif s[i] == "}":
            return None
        else:
            return string("fc_missing_comma")


def check_config_content_file(filepath: str) -> list:
    errors = []

    if _file_is_empty(filepath):
        return [string("fc_config_file_empty")]

    char_errors = _check_invalid_chars_file(filepath, ALLOWED_CONFIG_CHARS)
    if char_errors:
        return char_errors

    try:
        with open(filepath) as f:
            content = f.read()
    except OSError:
        return [string("fc_config_file_open_error")]

    dup = _find_duplicate_key(content)
    if dup is not None:
        errors.append(string("fc_duplicate_key").format(dup))
        return errors

    struct_err = _check_config_json_structure(content)
    if struct_err is not None:
        return [struct_err]

    try:
        cfg = json.loads(content)
    except Exception:
        return [string("fc_config_invalid_json")]

    if not isinstance(cfg, dict):
        return [string("fc_config_not_json_object")]

    unknown = set(cfg) - REQUIRED_CONFIG_KEYS - OPTIONAL_CONFIG_KEYS
    if unknown:
        errors.append(string("fc_unknown_params").format(", ".join(sorted(unknown))))

    missing = REQUIRED_CONFIG_KEYS - set(cfg)
    if missing:
        errors.append(string("fc_missing_params").format(", ".join(sorted(missing))))

    if errors:
        return errors

    nullable_keys = {"line_telegram", "destination_number_telegram", "destination_telegram", "stop_board_telegram"}
    str_keys = {"ap_name", "ap_password", "ap_ip"}
    bool_keys = {"show_start_and_end_stops", "force_short_names", "show_info_on_stop_board", "use_char_map"}
    int_keys = {"baudrate", "bits", "parity", "stop"}

    for key in nullable_keys:
        v = cfg[key]
        if v is not None and not isinstance(v, str):
            errors.append(string("fc_param_must_be_string_or_null").format(key))

    for key in str_keys:
        v = cfg[key]
        if not isinstance(v, str):
            errors.append(string("fc_param_must_be_string").format(key))
        elif not v:
            errors.append(string("fc_param_must_not_be_empty").format(key))

    for key in bool_keys:
        v = cfg[key]
        if not isinstance(v, bool):
            errors.append(string("fc_param_must_be_bool").format(key))

    for key in int_keys:
        v = cfg[key]
        if isinstance(v, bool) or not isinstance(v, int):
            errors.append(string("fc_param_must_be_int").format(key))

    nlt_data = cfg.get("nlt_data")
    if nlt_data is not None and not isinstance(nlt_data, str):
        errors.append(string("fc_param_must_be_string_or_null").format("nlt_data"))
    elif nlt_data == "":
        errors.append(string("fc_param_must_not_be_empty").format("nlt_data"))

    errors.extend(_check_displays(cfg))

    return errors


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _check_display(display, path: str) -> list:
    if not isinstance(display, dict):
        return [string("fc_param_must_be_object").format(path)]

    errors = []
    unknown = set(display) - DISPLAY_KEYS
    if unknown:
        errors.append(string("fc_unknown_params").format(", ".join(path + "." + key for key in sorted(unknown))))

    if "addr" not in display:
        errors.append(string("fc_missing_params").format(path + ".addr"))
    elif not _is_int(display["addr"]):
        errors.append(string("fc_param_must_be_int").format(path + ".addr"))
    elif not 1 <= display["addr"] <= MAX_DISPLAY_ADDR:
        errors.append(string("fc_param_must_be_one_of").format(path + ".addr", f"1..{MAX_DISPLAY_ADDR}"))

    for key in ("enabled", "show_start_and_end_stops"):
        if key in display and not isinstance(display[key], bool):
            errors.append(string("fc_param_must_be_bool").format(path + "." + key))

    for key, allowed in (("display_type", DISPLAY_TYPES), ("mode", DISPLAY_MODES)):
        if key in display and display[key] not in allowed:
            errors.append(string("fc_param_must_be_one_of").format(path + "." + key, ", ".join(allowed)))

    if "width" in display and not (_is_int(display["width"]) and display["width"] in DISPLAY_WIDTHS):
        widths = ", ".join(str(width) for width in DISPLAY_WIDTHS)
        errors.append(string("fc_param_must_be_one_of").format(path + ".width", widths))

    if "font" in display and not isinstance(display["font"], str):
        errors.append(string("fc_param_must_be_string").format(path + ".font"))

    return errors


def _check_displays(cfg) -> list:
    displays = cfg.get("displays")
    telegram = cfg.get("destination_telegram")
    addressed = telegram in ADDRESSED_TEXT_TELEGRAMS

    if displays is None:
        return [string("fc_missing_params").format("displays")] if addressed else []
    if not isinstance(displays, list):
        return [string("fc_param_must_be_list").format("displays")]

    errors = []
    seen_addresses = set()
    for index, display in enumerate(displays):
        display_errors = _check_display(display, f"displays[{index}]")
        errors.extend(display_errors)
        if display_errors:
            continue
        if display["addr"] in seen_addresses:
            errors.append(string("fc_duplicate_display_addr").format(display["addr"]))
        seen_addresses.add(display["addr"])

    if addressed and not errors and not any(display.get("enabled", True) for display in displays):
        errors.append(string("fc_no_enabled_display").format(telegram))

    return errors


def _is_special_char(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 99


def check_routes_content_file(filepath: str) -> list:
    errors = []

    if _file_is_empty(filepath):
        return [string("fc_routes_file_empty")]

    char_errors = _check_invalid_chars_file(filepath, ALLOWED_ROUTES_CHARS)
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
            errors.append(string("fc_field_wrong_data").format(line_num=line_num, field=field))

    def _require_field(rec, field: str):
        if field not in rec:
            errors.append(string("fc_missing_field").format(line_num=line_num, field=field))
            return None
        return rec[field]

    def _check_list_of_str(value, field: str):
        if value is None:
            return
        if not isinstance(value, list):
            errors.append(string("fc_field_must_be_list").format(line_num=line_num, field=field))
            return
        for item in value:
            if not isinstance(item, str):
                errors.append(string("fc_field_must_contain_strings").format(line_num=line_num, field=field))
                return

    try:
        with open(filepath) as f:
            for line in f:
                line_num += 1
                struct_err = _check_routes_ndjson_line_structure(line)
                if struct_err is not None:
                    errors.append(string("fc_at_line").format(line_num=line_num, err=struct_err))
                    if len(errors) >= 10:
                        errors.append(string("fc_more_errors"))
                        break
                    continue

                try:
                    rec = json.loads(line)
                except Exception:
                    errors.append(string("fc_routes_invalid_json").format(line_num))
                    continue

                for key in rec:
                    if line.count('"' + key + '":') > 1:
                        errors.append(string("fc_duplicate_route_key").format(line_num=line_num, key=key))
                        break

                if "id" in rec and "did" in rec:
                    errors.append(string("fc_id_and_did_both").format(line_num))
                    break
                elif "id" not in rec and "did" not in rec:
                    errors.append(string("fc_unknown_record_type").format(line_num))
                    break

                if "id" in rec:
                    unknown = set(rec) - {"id", "r", "nlt", "note", "sc"}
                    if unknown:
                        errors.append(
                            string("fc_unknown_fields").format(line_num=line_num, fields=", ".join(sorted(unknown)))
                        )
                    if current_route_id is not None and not current_route_has_dirs:
                        errors.append(string("fc_route_has_no_dirs").format(current_route_line))
                    _check_type(rec["id"], int, "id")
                    _check_type(_require_field(rec, "r"), str, "r")
                    if "nlt" in rec:
                        _check_type(rec["nlt"], bool, "nlt")
                    if "note" in rec:
                        _check_type(rec["note"], str, "note")
                    if rec.get("sc") is not None and not _is_special_char(rec["sc"]):
                        errors.append(string("fc_field_wrong_data").format(line_num=line_num, field="sc"))
                    if rec["id"] in seen_route_ids:
                        errors.append(string("fc_duplicate_route_id").format(line_num=line_num, route_id=rec["id"]))
                    else:
                        seen_route_ids.add(rec["id"])
                    current_route_id = rec["id"]
                    current_route_has_dirs = False
                    current_route_line = line_num

                if "did" in rec:
                    unknown = set(rec) - {"did", "p", "f", "s"}
                    if unknown:
                        errors.append(
                            string("fc_unknown_fields").format(line_num=line_num, fields=", ".join(sorted(unknown)))
                        )
                    _check_type(rec["did"], int, "did")

                    _check_type(_require_field(rec, "p"), int, "p")

                    _check_list_of_str(_require_field(rec, "f"), "f")
                    if "s" in rec:
                        _check_list_of_str(rec["s"], "s")

                    if "p" in rec:
                        if rec["p"] in seen_p_ids:
                            errors.append(string("fc_duplicate_dir_index").format(line_num=line_num, p_id=rec["p"]))
                        else:
                            seen_p_ids.add(rec["p"])

                    if current_route_id is None:
                        errors.append(string("fc_direction_without_route").format(line_num))
                    elif current_route_id != rec["did"]:
                        errors.append(
                            string("fc_direction_wrong_route").format(line_num=line_num, did=current_route_id)
                        )
                        if len(errors) >= 10:
                            errors.append(string("fc_more_errors"))
                            break

                    current_route_has_dirs = True

                if len(errors) >= 10:
                    errors.append(string("fc_more_errors"))
                    break

            if current_route_id is not None and not current_route_has_dirs:
                errors.append(string("fc_route_has_no_dirs").format(current_route_line))

    except OSError:
        return [string("fc_routes_file_open_error")]

    return errors


def assert_routes_match_config(routes_filepath, config_filepath):
    errors = []
    telegrams_list = []
    line_num = 0

    keys = [
        "line_telegram",
        "destination_number_telegram",
        "destination_telegram",
        "stop_board_telegram",
    ]

    try:
        with open(config_filepath) as file:
            try:
                data = json.load(file)
                for key, value in data.items():
                    if key in keys:
                        telegrams_list.append(value)
            except Exception:
                return [string("fc_config_invalid_json")]
    except OSError:
        return [string("fc_config_file_open_error")]

    try:
        with open(routes_filepath) as f:
            for line in f:
                line_num += 1
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if "id" in rec and rec.get("sc") is None:
                    if not rec["r"].isdigit() and "DS001neu" not in telegrams_list:
                        errors.append(
                            string("fc_wrong_route_number_format").format(line_num=line_num, route_number=rec["r"])
                        )
    except OSError:
        return [string("fc_routes_file_open_error")]

    return errors
