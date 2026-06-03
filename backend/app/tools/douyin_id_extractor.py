import json
import re
from urllib.parse import parse_qs, unquote, urlsplit

import httpx

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "douyin-id-extractor",
    "name": "抖音 UID / sec_uid 提取",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


# 同时覆盖 douyin.com 与 iesdouyin.com（分享短链跳转后的落地域名），允许多级子域名
URL_PATTERN = re.compile(r"(?i)\b(?:https?://)?(?:[\w-]+\.)*(?:ies)?douyin\.com/[^\s<>'\"]+")
SEC_UID_PATTERN = re.compile(r"\bMS4wLjAB[A-Za-z0-9._-]{12,}\b")
KEYED_SEC_UID_PATTERN = re.compile(r"(?i)(?:sec_uid|secUid)[\"'\s:=/?&%-]+([A-Za-z0-9._-]{16,})")
UID_KEY_PATTERN = re.compile(
    r"(?i)(?:uid|user_id|author_id|author_user_id|owner_id)[\"'\s:=/?&%-]+([0-9]{5,})"
)
UNIQUE_ID_PATTERN = re.compile(r"(?i)(?:unique_id|uniqueId|short_id|shortId)[\"'\s:=/?&%-]+([A-Za-z0-9._-]{2,})")
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        item = unquote(str(value)).strip().strip("\"' ")
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _normalize_url(url: str) -> str:
    value = url.strip()
    if not value.lower().startswith(("http://", "https://")):
        value = f"https://{value}"
    return value


def _extract_urls(text: str) -> list[str]:
    return _dedupe([_normalize_url(match.group(0)) for match in URL_PATTERN.finditer(text)])


def _extract_from_url(url: str) -> dict[str, list[str]]:
    parsed = urlsplit(url)
    decoded_url = unquote(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    sec_uids: list[str] = []
    uids: list[str] = []
    douyin_ids: list[str] = []

    segments = [unquote(item) for item in parsed.path.split("/") if item]
    for index, segment in enumerate(segments):
        if SEC_UID_PATTERN.fullmatch(segment):
            sec_uids.append(segment)
            continue
        if segment == "user" and index + 1 < len(segments):
            following = segments[index + 1]
            # /user/MS4w... 是 sec_uid；分享短链跳转后的 /share/user/{数字} 是真正的 uid
            if SEC_UID_PATTERN.fullmatch(following):
                sec_uids.append(following)
            elif following.isdigit() and len(following) >= 5:
                uids.append(following)

    for key, values in query.items():
        key_lower = key.lower()
        if key_lower in {"sec_uid", "secuid"}:
            sec_uids.extend(values)
        elif key_lower in {"uid", "user_id", "author_id", "author_user_id", "owner_id"}:
            uids.extend(values)
        elif key_lower in {"unique_id", "short_id", "douyin_id"}:
            douyin_ids.extend(values)

    sec_uids.extend(SEC_UID_PATTERN.findall(decoded_url))
    sec_uids.extend(KEYED_SEC_UID_PATTERN.findall(decoded_url))
    uids.extend(UID_KEY_PATTERN.findall(decoded_url))
    douyin_ids.extend(UNIQUE_ID_PATTERN.findall(decoded_url))

    return {
        "sec_uids": _dedupe(sec_uids),
        "uids": _dedupe(uids),
        "douyin_ids": _dedupe(douyin_ids),
    }


def _extract_from_text(text: str) -> dict[str, list[str]]:
    decoded = unquote(text)
    sec_uids = SEC_UID_PATTERN.findall(decoded) + KEYED_SEC_UID_PATTERN.findall(decoded)
    uids = UID_KEY_PATTERN.findall(decoded)
    douyin_ids = UNIQUE_ID_PATTERN.findall(decoded)
    for url in _extract_urls(decoded):
        from_url = _extract_from_url(url)
        sec_uids.extend(from_url["sec_uids"])
        uids.extend(from_url["uids"])
        douyin_ids.extend(from_url["douyin_ids"])
    return {
        "sec_uids": _dedupe(sec_uids),
        "uids": _dedupe(uids),
        "douyin_ids": _dedupe(douyin_ids),
    }


def _merge_result(target: dict[str, list[str]], source: dict[str, list[str]]) -> None:
    for key in target:
        target[key] = _dedupe(target[key] + source.get(key, []))


def _resolve_douyin_urls(urls: list[str]) -> list[dict[str, str]]:
    resolved = []
    with httpx.Client(timeout=8, headers=DEFAULT_HEADERS, follow_redirects=True, trust_env=False) as client:
        for url in urls:
            try:
                response = client.get(url)
                resolved.append(
                    {
                        "input_url": url,
                        "final_url": str(response.url),
                        "html": response.text[:300000],
                        "error": "",
                    }
                )
            except Exception as exc:
                resolved.append({"input_url": url, "final_url": url, "html": "", "error": str(exc)})
    return resolved


def _format_result(payload: dict[str, object]) -> str:
    lines = [
        "sec_uid:",
        "\n".join(payload["sec_uids"]) if payload["sec_uids"] else "未提取到",
        "",
        "uid:",
        "\n".join(payload["uids"]) if payload["uids"] else "未提取到",
        "",
        "抖音号/unique_id:",
        "\n".join(payload["douyin_ids"]) if payload["douyin_ids"] else "未提取到",
        "",
        "JSON:",
        json.dumps(payload, ensure_ascii=False, indent=2),
    ]
    notes = payload.get("notes") or []
    if notes:
        lines.extend(["", "说明:", *[f"- {note}" for note in notes]])
    return "\n".join(lines)


def run(text: str, resolve_links: bool = True, **_: dict) -> str:
    raw_text = text.strip()
    if not raw_text:
        raise AppException(message="请输入抖音主页链接、分享链接、uid 或 sec_uid", code=4001, status_code=400)

    result = _extract_from_text(raw_text)
    urls = _extract_urls(raw_text)
    resolved_urls: list[dict[str, str]] = []

    if resolve_links and urls:
        resolved_urls = _resolve_douyin_urls(urls)
        for item in resolved_urls:
            _merge_result(result, _extract_from_url(item["final_url"]))
            if item.get("html"):
                _merge_result(result, _extract_from_text(item["html"]))

    notes = []
    if urls and not resolve_links:
        notes.append("已关闭短链解析，仅从输入文本本身提取。")
    if not result["sec_uids"] and not result["uids"]:
        if result["douyin_ids"]:
            notes.append(
                "检测到抖音号（unique_id），但抖音号无法离线换算成 uid/sec_uid；"
                "请在该用户主页点「分享」复制链接，或粘贴形如 douyin.com/user/MS4w... 的主页链接再提取。"
            )
        else:
            notes.append("未提取到 uid/sec_uid，建议粘贴抖音主页链接，或用「分享」按钮复制的短链。")
    if any(item.get("error") for item in resolved_urls):
        notes.append("部分链接请求失败，可能被抖音风控或网络环境拦截。")

    payload = {
        "sec_uids": result["sec_uids"],
        "uids": result["uids"],
        "douyin_ids": result["douyin_ids"],
        "input_urls": urls,
        "resolved_urls": [
            {"input_url": item["input_url"], "final_url": item["final_url"], "error": item["error"]}
            for item in resolved_urls
        ],
        "notes": notes,
    }
    return _format_result(payload)
