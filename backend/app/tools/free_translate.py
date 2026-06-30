"""文件说明：实现「免费翻译」工具的后端逻辑。"""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "free-translate",
    "name": "免费翻译",
    "category": "ops",
    "input_mode": "text",
    "result_type": "text",
}

MYMEMORY_GET_URL = "https://api.mymemory.translated.net/get"
MAX_QUERY_BYTES = 500
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
}

SUPPORTED_LANGUAGES = {
    "zh-CN": "中文（简体）",
    "zh-TW": "中文（繁体）",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "de": "德语",
    "es": "西班牙语",
    "ru": "俄语",
    "pt": "葡萄牙语",
    "it": "意大利语",
    "ar": "阿拉伯语",
    "th": "泰语",
    "vi": "越南语",
    "id": "印尼语",
}


def _request_json(url: str, params: dict[str, Any]) -> Any:
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(full_url, headers=DEFAULT_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except TimeoutError as exc:
        raise AppException(message="翻译接口超时，请稍后重试", code=5001, status_code=502) from exc
    except urllib.error.URLError as exc:
        raise AppException(message=f"翻译接口连接失败：{exc.reason}", code=5001, status_code=502) from exc
    except json.JSONDecodeError as exc:
        raise AppException(message="翻译接口返回内容不是有效 JSON", code=5001, status_code=502) from exc


def _normalize_source_language(source_language: object) -> str:
    source = str(source_language or "en").strip()
    if source not in SUPPORTED_LANGUAGES:
        raise AppException(message="源语言不支持", code=4001, status_code=400)
    return source


def _normalize_target_language(target_language: object) -> str:
    target = str(target_language or "zh-CN").strip()
    if target not in SUPPORTED_LANGUAGES:
        raise AppException(message="目标语言不支持", code=4001, status_code=400)
    return target


def _normalize_mt(mt: object) -> str:
    if isinstance(mt, bool):
        return "1" if mt else "0"
    value = str(mt if mt is not None else "1").strip()
    if value not in {"0", "1"}:
        raise AppException(message="机器翻译开关参数不支持", code=4001, status_code=400)
    return value


def _validate_text(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise AppException(message="请输入需要翻译的文本", code=4001, status_code=400)
    byte_count = len(cleaned.encode("utf-8"))
    if byte_count > MAX_QUERY_BYTES:
        raise AppException(message=f"免费翻译接口单次最多支持 {MAX_QUERY_BYTES} UTF-8 字节，当前为 {byte_count} 字节", code=4001, status_code=400)
    return cleaned


def _format_match(match: Any) -> str:
    try:
        number = float(match)
    except (TypeError, ValueError):
        return "--"
    if number <= 1:
        return f"{number * 100:.0f}%"
    return f"{number:.0f}%"


def _extract_translation(payload: Any) -> tuple[str, Any]:
    if not isinstance(payload, dict):
        raise AppException(message="翻译接口返回格式异常", code=5001, status_code=502)
    if payload.get("quotaFinished") is True:
        raise AppException(message="免费翻译接口今日额度已用完，请稍后再试", code=5001, status_code=502)

    status = payload.get("responseStatus")
    response_data = payload.get("responseData") if isinstance(payload.get("responseData"), dict) else {}
    translated_text = str(response_data.get("translatedText") or "").strip()
    if status == 200 and translated_text:
        return translated_text, response_data.get("match")
    return "", response_data.get("match")


def _translate(query: str, source: str, target: str, mt: str) -> tuple[str, Any]:
    payload = _request_json(
        MYMEMORY_GET_URL,
        params={
            "q": query,
            "langpair": f"{source}|{target}",
            "mt": mt,
        },
    )
    return _extract_translation(payload)


def run(text: str, source_language: str = "en", target_language: str = "zh-CN", mt: object = "1", **_: dict) -> str:
    query = _validate_text(text)
    source = _normalize_source_language(source_language)
    target = _normalize_target_language(target_language)
    if source == target:
        raise AppException(message="源语言和目标语言不能相同", code=4001, status_code=400)

    mt_value = _normalize_mt(mt)
    translated_text, match = _translate(query, source, target, mt_value)
    if not translated_text and mt_value == "0":
        translated_text, match = _translate(query, source, target, "1")
    if not translated_text:
        raise AppException(message="翻译接口没有返回有效结果", code=5001, status_code=502)

    return "\n".join(
        [
            "翻译结果",
            translated_text,
            "",
            "请求信息",
            f"匹配度：{_format_match(match)}",
            f"输入 UTF-8 字节数：{len(query.encode('utf-8'))}/{MAX_QUERY_BYTES}",
        ]
    )
