"""文件说明：实现「JSON 和 URL 参数互转」工具的后端逻辑。"""

import json
from urllib.parse import parse_qs, urlencode, urlsplit

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "json-url-params",
    "name": "JSON 与 URL 参数互转",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def _json_to_params(text: str) -> str:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AppException(message=f"JSON 格式无效：{exc.msg}", code=4001, status_code=400) from exc

    if not isinstance(parsed, dict):
        raise AppException(message="JSON 输入必须是对象", code=4001, status_code=400)

    normalized = {}
    for key, value in parsed.items():
        if isinstance(value, list):
            normalized[str(key)] = [json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else "" if item is None else str(item) for item in value]
        elif isinstance(value, dict):
            normalized[str(key)] = json.dumps(value, ensure_ascii=False)
        elif value is None:
            normalized[str(key)] = ""
        else:
            normalized[str(key)] = str(value)

    return urlencode(normalized, doseq=True)


def _params_to_json(text: str) -> str:
    query = urlsplit(text).query if "://" in text or "?" in text else text
    parsed = parse_qs(query, keep_blank_values=True)
    normalized = {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
    return json.dumps(normalized, ensure_ascii=False, indent=2)


def run(text: str, action: str = "json_to_params", **_: dict) -> str:
    if action == "json_to_params":
        return _json_to_params(text)
    if action == "params_to_json":
        return _params_to_json(text)
    raise AppException(message="操作方式无效", code=4001, status_code=400)
