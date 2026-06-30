"""文件说明：实现「JWT 解码」工具的后端逻辑。"""

import base64
import json
from datetime import datetime, timezone

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "jwt-decoder",
    "name": "JWT 解码",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def _decode_segment(segment: str) -> str:
    padding = "=" * (-len(segment) % 4)
    try:
        return base64.urlsafe_b64decode(segment + padding).decode("utf-8")
    except Exception as exc:
        raise AppException(message="JWT 分段内容无效", code=4001, status_code=400) from exc


def run(text: str, **_: dict) -> str:
    token = text.strip()
    parts = token.split(".")
    if len(parts) != 3:
        raise AppException(message="JWT 必须包含 3 段内容", code=4001, status_code=400)

    try:
        header = json.loads(_decode_segment(parts[0]))
    except json.JSONDecodeError as exc:
        raise AppException(message=f"JWT Header 的 JSON 格式无效：{exc.msg}", code=4001, status_code=400) from exc

    try:
        payload = json.loads(_decode_segment(parts[1]))
    except json.JSONDecodeError:
        payload = {"raw": _decode_segment(parts[1])}

    exp_text = None
    if isinstance(payload, dict) and isinstance(payload.get("exp"), (int, float)):
        exp_text = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).isoformat()

    result = {
        "header": header,
        "payload": payload,
        "signature": parts[2],
        "signature_length": len(parts[2]),
        "exp_utc": exp_text,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)
