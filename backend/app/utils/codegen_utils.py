import json
import re

from app.core.exceptions import AppException


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load_json_value(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise AppException(message=f"JSON 格式无效：{exc.msg}", code=4001, status_code=400) from exc


def ensure_object_schema(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, list) and value:
        first = next((item for item in value if isinstance(item, dict)), None)
        if first is not None:
            return first
    raise AppException(message="该工具需要 JSON 对象或对象数组", code=4001, status_code=400)


def split_words(name: str) -> list[str]:
    raw = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(name))
    return [part for part in re.split(r"[^A-Za-z0-9]+", raw) if part]


def pascal_case(name: str, default: str = "Root") -> str:
    parts = split_words(name)
    if not parts:
        return default
    value = "".join(part[:1].upper() + part[1:] for part in parts)
    return f"N{value}" if value[:1].isdigit() else value


def camel_case(name: str, default: str = "field") -> str:
    parts = split_words(name)
    if not parts:
        return default
    head = parts[0].lower()
    tail = "".join(part[:1].upper() + part[1:] for part in parts[1:])
    value = head + tail
    return f"{default}{value[:1].upper()}{value[1:]}" if value[:1].isdigit() else value


def snake_case(name: str, default: str = "field") -> str:
    parts = split_words(name)
    if not parts:
        return default
    value = "_".join(part.lower() for part in parts)
    return f"{default}_{value}" if value[:1].isdigit() else value


def safe_ts_property_name(name: str) -> str:
    return name if _IDENTIFIER_RE.match(name) else json.dumps(name, ensure_ascii=False)
