"""文件说明：实现「Bcrypt 加密/校验」工具的后端逻辑。"""

import json

import bcrypt

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "bcrypt-tool",
    "name": "Bcrypt 加密/校验",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, action: str = "hash", rounds: int = 12, hash_value: str = "", **_: dict) -> str:
    if action == "hash":
        try:
            rounds = int(rounds)
        except (TypeError, ValueError) as exc:
            raise AppException(message="轮数必须是整数", code=4001, status_code=400) from exc
        if rounds < 4 or rounds > 16:
            raise AppException(message="轮数必须在 4 到 16 之间", code=4001, status_code=400)
        return bcrypt.hashpw(text.encode("utf-8"), bcrypt.gensalt(rounds)).decode("utf-8")

    if action == "verify":
        if not hash_value:
            raise AppException(message="校验模式下必须提供 bcrypt 哈希值", code=4001, status_code=400)
        try:
            matched = bcrypt.checkpw(text.encode("utf-8"), hash_value.encode("utf-8"))
        except Exception as exc:
            raise AppException(message="bcrypt 哈希值无效", code=4001, status_code=400) from exc
        return json.dumps({"matched": matched}, ensure_ascii=False, indent=2)

    raise AppException(message="操作方式无效", code=4001, status_code=400)
