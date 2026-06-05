import json
import re
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

import httpx

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "market-quote",
    "name": "股票基金实时行情",
    "category": "other",
    "input_mode": "form",
    "result_type": "text",
}


EASTMONEY_FIELDS = ",".join(
    [
        "f43",
        "f44",
        "f45",
        "f46",
        "f47",
        "f48",
        "f57",
        "f58",
        "f59",
        "f60",
        "f86",
        "f107",
        "f116",
        "f117",
        "f168",
        "f169",
        "f170",
        "f171",
    ]
)
EASTMONEY_URL = "https://push2.eastmoney.com/api/qt/stock/get"
EASTMONEY_ULIST_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
EASTMONEY_SUGGEST_URL = "https://searchapi.eastmoney.com/api/suggest/get"
EASTMONEY_TRENDS_URL = "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
EASTMONEY_KLINE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
SINA_KLINE_URL = "https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData"
SINA_HQ_URL = "https://hq.sinajs.cn/list="
FUND_URL_TEMPLATE = "https://fundgz.1234567.com.cn/js/{code}.js"
EASTMONEY_UT_TOKEN = "fa5fd1943c7b386f172d6893dbfba10b"
EASTMONEY_SEARCH_TOKEN = "D43BF722C8E33C743DEC4FA52FCA5277"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://quote.eastmoney.com/",
}
SINA_HEADERS = {
    "User-Agent": DEFAULT_HEADERS["User-Agent"],
    "Accept": DEFAULT_HEADERS["Accept"],
    "Referer": "https://finance.sina.com.cn/",
}
MAX_SYMBOLS = 8
MAX_CHART_POINTS = 150
# 非精确匹配（前缀/包含）时要求的最少中文字数，避免“中证”“白酒”这类过短输入被误判
MIN_FUZZY_NAME_LEN = 4
EASTMONEY_ULIST_FIELDS = ",".join(
    [
        "f1",
        "f2",
        "f3",
        "f4",
        "f5",
        "f6",
        "f7",
        "f8",
        "f12",
        "f13",
        "f14",
        "f15",
        "f16",
        "f17",
        "f18",
        "f20",
        "f21",
        "f124",
        "f152",
    ]
)
EASTMONEY_TRENDS_FIELDS1 = "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
EASTMONEY_TRENDS_FIELDS2 = "f51,f52,f53,f54,f55,f56,f57,f58"
EASTMONEY_KLINE_FIELDS1 = "f1,f2,f3,f4,f5,f6"
EASTMONEY_KLINE_FIELDS2 = "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"


def _split_symbols(text: str) -> list[str]:
    items = re.split(r"[\s,，;；、]+", text.strip())
    return [item.strip() for item in items if item.strip()]


def _normalize_symbol(value: str) -> str:
    return value.strip().upper().replace(" ", "")


def _normalize_name(value: str) -> str:
    return re.sub(r"\s+", "", value.strip()).upper()


def _contains_cjk(value: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff]", value))


def _is_fund_like_code(symbol: str) -> bool:
    return bool(re.fullmatch(r"\d{6}", symbol)) and not symbol.startswith(("0", "3", "4", "5", "6", "8", "9", "15", "16", "18"))


def _market_allows(quote_id: str, classify: str, market: str) -> bool:
    if market == "fund":
        return quote_id.startswith("150.") or "FUND" in classify.upper() or "基金" in classify
    if market in {"cn", "hk", "us"}:
        market_prefix = {"cn": ("0.", "1.", "2."), "hk": ("116.",), "us": ("105.", "106.")}[market]
        return quote_id.startswith(market_prefix)
    return True


def _name_match_score(query_norm: str, name_norm: str) -> int | None:
    """越小越精确：0 完全相等 / 1 候选名以输入开头 / 2 输入以候选名开头 / 3 输入是候选名子串。"""
    if not name_norm:
        return None
    if name_norm == query_norm:
        return 0
    if name_norm.startswith(query_norm):
        return 1
    if query_norm.startswith(name_norm):
        return 2
    if query_norm in name_norm:
        return 3
    return None


def _search_full_name(symbol: str, market: str, client: httpx.Client) -> tuple[dict[str, str] | None, str | None]:
    if not _contains_cjk(symbol):
        return None, None
    try:
        response = client.get(
            EASTMONEY_SUGGEST_URL,
            params={"input": symbol.strip(), "type": 14, "count": 10, "token": EASTMONEY_SEARCH_TOKEN},
            headers={**DEFAULT_HEADERS, "Referer": "https://www.eastmoney.com/"},
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return None, f"名称搜索失败：{exc}"

    table = payload.get("QuotationCodeTable") if isinstance(payload, dict) else None
    rows = table.get("Data") if isinstance(table, dict) else []
    if not isinstance(rows, list):
        rows = []
    if not rows:
        return None, "请输入完整的股票基金名称"

    query_norm = _normalize_name(symbol)
    query_cjk_len = len(re.findall(r"[㐀-鿿]", symbol))

    best: tuple[tuple[int, int], dict, str, str, str, str] | None = None
    for item in rows:
        if not isinstance(item, dict):
            continue
        quote_id = str(item.get("QuoteID") or "")
        code = str(item.get("Code") or item.get("UnifiedCode") or "")
        classify = str(item.get("Classify") or item.get("SecurityTypeName") or "")
        if not quote_id or not code or not _market_allows(quote_id, classify, market):
            continue

        raw_name = str(item.get("Name") or "")
        scores = []
        for candidate_name in (raw_name, str(item.get("SHORTNAME") or "")):
            candidate_norm = _normalize_name(candidate_name)
            score = _name_match_score(query_norm, candidate_norm)
            if score is not None:
                scores.append((score, len(candidate_norm)))
        if not scores:
            continue

        score, name_len = min(scores)
        # 非精确匹配时，过短的输入（如“中证”）视为名称不完整，提示用户补全
        if score != 0 and query_cjk_len < MIN_FUZZY_NAME_LEN:
            continue

        rank = (score, name_len)
        if best is None or rank < best[0]:
            best = (rank, item, quote_id, code, classify, raw_name)

    if best is None:
        return None, "请输入完整的股票基金名称"

    _rank, _item, quote_id, code, classify, raw_name = best
    return {
        "code": code,
        "name": raw_name or symbol,
        "quote_id": quote_id,
        "classify": classify,
    }, None


def _eastmoney_candidates(symbol: str, market: str = "auto") -> list[tuple[str, str]]:
    normalized = _normalize_symbol(symbol)
    candidates: list[tuple[str, str]] = []

    if re.fullmatch(r"\d{1,3}\.[A-Z0-9.]+", normalized):
        return [(normalized, "显式 secid")]

    suffix_match = re.fullmatch(r"(\d{6})\.(SH|SZ|BJ)", normalized)
    if suffix_match:
        code, exchange = suffix_match.groups()
        return [(f"{1 if exchange == 'SH' else 0}.{code}", exchange)]

    prefix_match = re.fullmatch(r"(SH|SZ|BJ)(\d{6})", normalized)
    if prefix_match:
        exchange, code = prefix_match.groups()
        return [(f"{1 if exchange == 'SH' else 0}.{code}", exchange)]

    hk_suffix = re.fullmatch(r"(\d{1,5})\.HK", normalized)
    hk_prefix = re.fullmatch(r"HK(\d{1,5})", normalized)
    if hk_suffix or hk_prefix:
        code = (hk_suffix or hk_prefix).group(1).zfill(5)
        return [(f"116.{code}", "港股")]

    us_suffix = re.fullmatch(r"([A-Z][A-Z0-9.]{0,9})\.US", normalized)
    us_prefix = re.fullmatch(r"US([A-Z][A-Z0-9.]{0,9})", normalized)
    market_prefix = re.fullmatch(r"(NASDAQ|NYSE|AMEX):([A-Z][A-Z0-9.]{0,9})", normalized)
    if us_suffix or us_prefix or market_prefix:
        code = (us_suffix or us_prefix or market_prefix).group(1 if not market_prefix else 2)
        if market_prefix and market_prefix.group(1) == "NYSE":
            return [(f"106.{code}", "美股")]
        return [(f"105.{code}", "美股"), (f"106.{code}", "美股")]

    if re.fullmatch(r"\d{6}", normalized):
        if normalized.startswith(("6", "5", "9")):
            candidates.append((f"1.{normalized}", "沪市"))
        if normalized.startswith("9"):
            candidates.append((f"2.{normalized}", "指数"))
        if normalized.startswith(("0", "2", "3", "4", "8", "15", "16", "18")):
            candidates.append((f"0.{normalized}", "深北"))

    if re.fullmatch(r"\d{1,5}", normalized) and not candidates and market in {"auto", "hk"}:
        candidates.append((f"116.{normalized.zfill(5)}", "港股"))

    if re.fullmatch(r"[A-Z][A-Z0-9.]{0,9}", normalized) and market in {"auto", "us"}:
        candidates.extend([(f"105.{normalized}", "美股"), (f"106.{normalized}", "美股")])

    return candidates


def _scale(value: Any, decimals: int = 2) -> float | None:
    if value in {None, "-", ""}:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number / (10 ** decimals), decimals)


def _plain_number(value: Any) -> float | None:
    if value in {None, "-", ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_number(value: Any) -> int | None:
    if value in {None, "-", ""}:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _format_timestamp(value: Any) -> str:
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return ""
    if timestamp <= 0:
        return ""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def _request_any_json(
    client: httpx.Client,
    url: str,
    params: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: float = 8,
) -> Any:
    request_headers = headers or DEFAULT_HEADERS
    try:
        response = client.get(url, params=params, headers=request_headers, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, (dict, list)):
            return payload
    except Exception:
        pass

    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{url}?{query}",
        headers={
            "User-Agent": request_headers.get("User-Agent", DEFAULT_HEADERS["User-Agent"]),
            "Accept": request_headers.get("Accept", DEFAULT_HEADERS["Accept"]),
            "Referer": request_headers.get("Referer", DEFAULT_HEADERS["Referer"]),
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
    return json.loads(body)


def _request_json(
    client: httpx.Client,
    url: str,
    params: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: float = 8,
) -> dict[str, Any]:
    payload = _request_any_json(client, url, params, headers, timeout)
    if not isinstance(payload, dict):
        raise ValueError("JSON 根节点不是对象")
    return payload


def _request_text(
    client: httpx.Client,
    url: str,
    headers: dict[str, str] | None = None,
    encoding: str = "utf-8",
    timeout: float = 8,
) -> str:
    request_headers = headers or DEFAULT_HEADERS
    try:
        response = client.get(url, headers=request_headers, timeout=timeout)
        response.raise_for_status()
        return response.content.decode(encoding, errors="replace")
    except Exception:
        pass

    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode(encoding, errors="replace")


def _sample_chart_points(points: list[list[Any]], max_points: int = MAX_CHART_POINTS) -> list[list[Any]]:
    if len(points) <= max_points:
        return points
    if max_points <= 2:
        return [points[0], points[-1]]

    sampled: list[list[Any]] = []
    last_index = -1
    step = (len(points) - 1) / (max_points - 1)
    for position in range(max_points):
        index = round(position * step)
        if index == last_index:
            continue
        sampled.append(points[index])
        last_index = index
    if sampled[-1] is not points[-1]:
        sampled[-1] = points[-1]
    return sampled


def _parse_trend_item(value: Any) -> list[Any] | None:
    if not isinstance(value, str):
        return None

    parts = value.split(",")
    if len(parts) < 8:
        return None

    time_text = parts[0].strip()
    price = _plain_number(parts[2])
    avg_price = _plain_number(parts[7])
    volume = _plain_number(parts[5])
    if price is None:
        return None

    chart_time = time_text[:16] if len(time_text) >= 16 else time_text
    return [
        chart_time,
        price,
        avg_price,
        volume or 0,
    ]


def _parse_kline_item(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None

    parts = value.split(",")
    if len(parts) < 6:
        return None

    date_text = parts[0].strip()
    close = _plain_number(parts[2])
    if not date_text or close is None:
        return None

    return {
        "date": date_text,
        "open": _plain_number(parts[1]),
        "close": close,
        "high": _plain_number(parts[3]),
        "low": _plain_number(parts[4]),
        "volume": _plain_number(parts[5]) or 0,
        "amount": _plain_number(parts[6]) if len(parts) > 6 else None,
    }


def _parse_sina_kline_item(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None

    time_text = str(value.get("day") or "").strip()
    close = _plain_number(value.get("close"))
    if not time_text or close is None:
        return None

    return {
        "time": time_text,
        "date": time_text[:10],
        "open": _plain_number(value.get("open")),
        "close": close,
        "high": _plain_number(value.get("high")),
        "low": _plain_number(value.get("low")),
        "volume": _plain_number(value.get("volume")) or 0,
        "amount": _plain_number(value.get("amount")),
    }


def _sina_cn_symbol(secid: str) -> str | None:
    market_prefix, _, code = secid.partition(".")
    code = code.strip().upper()
    if not re.fullmatch(r"\d{6}", code):
        return None
    if market_prefix in {"105", "106", "116", "150"}:
        return None
    if market_prefix == "2":
        return f"si{code}"
    if market_prefix == "1" or code.startswith(("5", "6", "9")):
        return f"sh{code}"
    return f"sz{code}"


def _parse_sina_quote_text(text: str, code: str) -> dict[str, Any] | None:
    match = re.search(r'var hq_str_[^=]+="(.*?)";', text.strip(), re.S)
    if not match:
        return None

    parts = match.group(1).split(",")
    if len(parts) < 32 or not parts[0]:
        return None

    latest = _plain_number(parts[3])
    previous_close = _plain_number(parts[2])
    date_text = parts[30].strip()
    time_text = parts[31].strip()
    return {
        "code": code,
        "name": parts[0].strip() or code,
        "open": _plain_number(parts[1]),
        "previous_close": previous_close,
        "latest": latest if latest not in {None, 0} else previous_close,
        "high": _plain_number(parts[4]),
        "low": _plain_number(parts[5]),
        "volume": _plain_number(parts[8]),
        "amount": _plain_number(parts[9]),
        "updated_at": f"{date_text} {time_text}".strip(),
    }


def _query_sina_cn_quote_data(secid: str, client: httpx.Client) -> dict[str, Any] | None:
    sina_symbol = _sina_cn_symbol(secid)
    if not sina_symbol:
        return None

    try:
        text = _request_text(
            client,
            f"{SINA_HQ_URL}{sina_symbol}",
            headers=SINA_HEADERS,
            encoding="gbk",
            timeout=4,
        )
    except Exception:
        return None

    _market_prefix, _, code = secid.partition(".")
    return _parse_sina_quote_text(text, code)


def _query_intraday_chart(secid: str, client: httpx.Client) -> dict[str, Any] | None:
    try:
        payload = _request_json(
            client,
            EASTMONEY_TRENDS_URL,
            params={
                "secid": secid,
                "fields1": EASTMONEY_TRENDS_FIELDS1,
                "fields2": EASTMONEY_TRENDS_FIELDS2,
                "ut": EASTMONEY_UT_TOKEN,
                "ndays": 1,
                "iscr": 0,
                "iscca": 0,
            },
            timeout=4,
        )
    except Exception:
        return None

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return None

    raw_trends = data.get("trends")
    if not isinstance(raw_trends, list):
        return None

    points = [point for point in (_parse_trend_item(item) for item in raw_trends) if point]
    if len(points) < 2:
        return None

    pre_close = _plain_number(data.get("preClose"))
    if pre_close is None:
        pre_close = _plain_number(data.get("prePrice"))

    start_time = str(points[0][0])
    end_time = str(points[-1][0])
    trade_date = start_time[:10] if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", start_time) else ""

    return {
        "kind": "intraday",
        "point_format": ["time", "price", "avg_price", "volume"],
        "code": str(data.get("code") or ""),
        "name": str(data.get("name") or ""),
        "market_code": _int_number(data.get("market")),
        "points": _sample_chart_points(points),
        "point_count": len(points),
        "sampled": len(points) > MAX_CHART_POINTS,
        "pre_close": pre_close,
        "start_time": start_time,
        "end_time": end_time,
        "trade_date": trade_date,
        "time_range": f"{start_time} - {end_time}" if start_time and end_time else "",
        "updated_at": _format_timestamp(data.get("time")),
        "source": "东方财富分时行情",
        "source_url": f"{EASTMONEY_TRENDS_URL}?secid={secid}",
    }


def _query_daily_kline_chart(secid: str, client: httpx.Client) -> dict[str, Any] | None:
    try:
        payload = _request_json(
            client,
            EASTMONEY_KLINE_URL,
            params={
                "secid": secid,
                "fields1": EASTMONEY_KLINE_FIELDS1,
                "fields2": EASTMONEY_KLINE_FIELDS2,
                "ut": EASTMONEY_UT_TOKEN,
                "klt": 101,
                "fqt": 1,
                "beg": f"{datetime.now().year - 1}0101",
                "end": "20500101",
            },
            timeout=4,
        )
    except Exception:
        return None

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return None

    raw_klines = data.get("klines")
    if not isinstance(raw_klines, list):
        return None

    parsed_items = [item for item in (_parse_kline_item(value) for value in raw_klines) if item]
    if len(parsed_items) < 2:
        return None

    visible_items = parsed_items[-MAX_CHART_POINTS:]
    points = []
    for index, item in enumerate(visible_items):
        window = visible_items[max(0, index - 4) : index + 1]
        close_values = [_plain_number(row.get("close")) for row in window]
        close_values = [value for value in close_values if value is not None]
        ma5 = round(sum(close_values) / len(close_values), 4) if close_values else None
        points.append([item["date"], item["close"], ma5, item["volume"]])

    latest_bar = visible_items[-1]
    previous_bar = parsed_items[-2]
    start_time = str(points[0][0])
    end_time = str(points[-1][0])

    return {
        "kind": "daily_kline",
        "point_format": ["date", "close", "ma5", "volume"],
        "code": str(data.get("code") or ""),
        "name": str(data.get("name") or ""),
        "market_code": _int_number(data.get("market")),
        "points": points,
        "point_count": len(parsed_items),
        "sampled": len(parsed_items) > MAX_CHART_POINTS,
        "pre_close": previous_bar.get("close"),
        "start_time": start_time,
        "end_time": end_time,
        "trade_date": end_time,
        "time_range": f"{start_time} - {end_time}",
        "updated_at": end_time,
        "source": "东方财富日K行情",
        "source_url": f"{EASTMONEY_KLINE_URL}?secid={secid}",
        "latest_bar": latest_bar,
        "previous_bar": previous_bar,
    }


def _query_sina_intraday_kline_chart(secid: str, client: httpx.Client) -> dict[str, Any] | None:
    sina_symbol = _sina_cn_symbol(secid)
    if not sina_symbol:
        return None

    try:
        payload = _request_any_json(
            client,
            SINA_KLINE_URL,
            params={"symbol": sina_symbol, "scale": 5, "ma": "no", "datalen": 96},
            headers=SINA_HEADERS,
            timeout=4,
        )
    except Exception:
        return None

    if not isinstance(payload, list):
        return None

    parsed_items = [item for item in (_parse_sina_kline_item(value) for value in payload) if item]
    if len(parsed_items) < 2:
        return None

    grouped_items: dict[str, list[dict[str, Any]]] = {}
    for item in parsed_items:
        date_text = str(item.get("date") or "")
        if date_text:
            grouped_items.setdefault(date_text, []).append(item)

    available_dates = list(grouped_items)
    if not available_dates:
        return None

    latest_date = available_dates[-1]
    selected_date = next((date for date in reversed(available_dates) if len(grouped_items[date]) >= 2), "")
    if not selected_date:
        return None

    visible_items = grouped_items[selected_date][-MAX_CHART_POINTS:]
    display_note = "当前交易日K线数据不足，展示上一交易日" if selected_date != latest_date else ""

    points = []
    for index, item in enumerate(visible_items):
        window = visible_items[max(0, index - 4) : index + 1]
        close_values = [_plain_number(row.get("close")) for row in window]
        close_values = [value for value in close_values if value is not None]
        ma5 = round(sum(close_values) / len(close_values), 4) if close_values else None
        points.append([item["time"], item["close"], ma5, item["volume"]])

    sampled_points = _sample_chart_points(points)
    quote_data = _query_sina_cn_quote_data(secid, client) or {}
    quote_date = str(quote_data.get("updated_at") or "")[:10]
    quote_matches_chart = bool(quote_date and quote_date == selected_date)
    _market_prefix, _, code = secid.partition(".")
    market_code = _int_number(_market_prefix)
    latest_bar = visible_items[-1]
    high_values = [_plain_number(item.get("high")) for item in visible_items]
    low_values = [_plain_number(item.get("low")) for item in visible_items]
    high_values = [value for value in high_values if value is not None]
    low_values = [value for value in low_values if value is not None]

    start_time = str(sampled_points[0][0])
    end_time = str(sampled_points[-1][0])
    pre_close = _plain_number(quote_data.get("previous_close"))

    return {
        "kind": "intraday_kline",
        "point_format": ["time", "close", "ma5", "volume"],
        "code": code,
        "name": str(quote_data.get("name") or code),
        "market_code": market_code,
        "points": sampled_points,
        "point_count": len(visible_items),
        "sampled": len(visible_items) > MAX_CHART_POINTS,
        "pre_close": pre_close if quote_matches_chart else None,
        "start_time": start_time,
        "end_time": end_time,
        "trade_date": selected_date,
        "time_range": f"{start_time} - {end_time}",
        "updated_at": quote_data.get("updated_at") if quote_matches_chart else end_time,
        "source": "新浪财经5分钟K线",
        "source_url": f"{SINA_KLINE_URL}?symbol={sina_symbol}&scale=5&datalen=96",
        "display_note": display_note,
        "latest_bar": {
            "date": selected_date,
            "open": (_plain_number(quote_data.get("open")) if quote_matches_chart else None) or visible_items[0].get("open"),
            "close": (_plain_number(quote_data.get("latest")) if quote_matches_chart else None) or latest_bar.get("close"),
            "high": (_plain_number(quote_data.get("high")) if quote_matches_chart else None) or (max(high_values) if high_values else None),
            "low": (_plain_number(quote_data.get("low")) if quote_matches_chart else None) or (min(low_values) if low_values else None),
            "volume": (_plain_number(quote_data.get("volume")) if quote_matches_chart else None)
            or sum(_plain_number(item.get("volume")) or 0 for item in visible_items),
            "amount": _plain_number(quote_data.get("amount")) if quote_matches_chart else None,
        },
    }


def _build_quote_snapshot_chart(card: dict[str, Any], secid: str) -> dict[str, Any] | None:
    latest = _plain_number(card.get("latest"))
    if latest is None:
        return None

    updated_at = str(card.get("updated_at") or "")
    matched = re.match(r"^(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}))?", updated_at)
    trade_date = matched.group(1) if matched else datetime.now().strftime("%Y-%m-%d")
    end_clock = matched.group(2) if matched and matched.group(2) else "15:00"
    start_time = f"{trade_date} 09:30"
    end_time = f"{trade_date} {end_clock}"
    if end_time <= start_time:
        end_time = f"{trade_date} 15:00"

    open_price = _plain_number(card.get("open")) or _plain_number(card.get("previous_close")) or latest
    previous_close = _plain_number(card.get("previous_close"))
    volume = _plain_number(card.get("volume")) or 0
    _market_prefix, _, _code = secid.partition(".")

    return {
        "kind": "quote_snapshot",
        "point_format": ["time", "price", "reference", "volume"],
        "code": str(card.get("symbol") or ""),
        "name": str(card.get("name") or card.get("symbol") or ""),
        "market_code": _int_number(_market_prefix),
        "points": [[start_time, open_price, None, 0], [end_time, latest, None, volume]],
        "point_count": 2,
        "sampled": False,
        "pre_close": previous_close,
        "start_time": start_time,
        "end_time": end_time,
        "trade_date": trade_date,
        "time_range": f"{start_time} - {end_time}",
        "updated_at": updated_at or end_time,
        "source": "当前报价快照",
        "source_url": str(card.get("source_url") or ""),
        "latest_bar": {
            "date": trade_date,
            "open": open_price,
            "close": latest,
            "high": _plain_number(card.get("high")) or max(open_price, latest),
            "low": _plain_number(card.get("low")) or min(open_price, latest),
            "volume": volume,
            "amount": _plain_number(card.get("amount")),
        },
    }


def _attach_intraday_chart(card: dict[str, Any], secid: str, client: httpx.Client) -> dict[str, Any]:
    chart = (
        _query_intraday_chart(secid, client)
        or _query_daily_kline_chart(secid, client)
        or _query_sina_intraday_kline_chart(secid, client)
        or _build_quote_snapshot_chart(card, secid)
    )
    if chart:
        card["chart"] = chart
    return card


def _query_eastmoney_trends_quote(secid: str, client: httpx.Client) -> tuple[dict[str, Any] | None, str | None]:
    chart = (
        _query_intraday_chart(secid, client)
        or _query_daily_kline_chart(secid, client)
        or _query_sina_intraday_kline_chart(secid, client)
    )
    if not chart:
        return None, f"{secid} 图表端点暂无数据"

    _market_prefix, _, secid_code = secid.partition(".")
    code = str(chart.get("code") or secid_code)
    name = str(chart.get("name") or code)
    market_code = _int_number(chart.get("market_code"))
    if market_code is None:
        market_code = _int_number(_market_prefix)
    market_label, market_region, currency = _market_label(market_code, code)

    latest_bar = chart.get("latest_bar") if isinstance(chart.get("latest_bar"), dict) else {}
    points = chart.get("points") if isinstance(chart.get("points"), list) else []
    prices = [_plain_number(point[1]) for point in points if isinstance(point, list) and len(point) > 1]
    prices = [price for price in prices if price is not None]
    if len(prices) < 2:
        return None, f"{secid} 图表端点暂无有效价格"

    latest = _plain_number(latest_bar.get("close")) or prices[-1]
    previous_close = _plain_number(chart.get("pre_close"))
    change = round(latest - previous_close, 4) if previous_close else None
    change_percent = round(change / previous_close * 100, 2) if change is not None and previous_close else None

    card = {
        "kind": "quote",
        "asset_type": _asset_type(code, market_code, name),
        "symbol": code,
        "name": name,
        "market": market_label,
        "market_region": market_region,
        "currency": currency,
        "latest": latest,
        "change": change,
        "change_percent": change_percent,
        "open": _plain_number(latest_bar.get("open")) or prices[0],
        "high": _plain_number(latest_bar.get("high")) or max(prices),
        "low": _plain_number(latest_bar.get("low")) or min(prices),
        "previous_close": previous_close,
        "volume": _plain_number(latest_bar.get("volume"))
        or sum(_plain_number(point[3]) or 0 for point in points if isinstance(point, list) and len(point) > 3),
        "amount": _plain_number(latest_bar.get("amount")),
        "updated_at": chart.get("updated_at") or chart.get("end_time") or "",
        "source": chart.get("source") or "东方财富图表行情",
        "provider": "sina" if str(chart.get("source") or "").startswith("新浪") else "eastmoney",
        "source_url": chart.get("source_url") or f"{EASTMONEY_KLINE_URL}?secid={secid}",
        "chart": chart,
    }
    return card, None


def _market_label(market_code: int | None, code: str) -> tuple[str, str, str]:
    if market_code == 116:
        return "港股", "HK", "HKD"
    if market_code == 105:
        return "纳斯达克", "US", "USD"
    if market_code == 106:
        return "纽交所/美股", "US", "USD"
    if market_code == 1:
        return "沪市", "CN", "CNY"
    if market_code == 2:
        return "指数", "CN", "CNY"
    if market_code == 0 and code.startswith(("4", "8")):
        return "北交所", "CN", "CNY"
    if market_code == 0:
        return "深市", "CN", "CNY"
    return "公开行情", "AUTO", "CNY"


def _asset_type(code: str, market_code: int | None, name: str) -> str:
    if market_code == 116:
        return "港股"
    if market_code in {105, 106}:
        return "美股"
    if market_code == 2 or (code.startswith(("000", "399", "93")) and "ETF" not in name.upper()):
        return "指数"
    if code.startswith(("5", "15", "16", "18")) or "ETF" in name.upper() or "LOF" in name.upper():
        return "场内基金"
    return "股票"


def _query_eastmoney_ulist(secid: str, client: httpx.Client) -> tuple[dict[str, Any] | None, str | None]:
    try:
        response = client.get(
            EASTMONEY_ULIST_URL,
            params={"secids": secid, "fields": EASTMONEY_ULIST_FIELDS, "ut": EASTMONEY_UT_TOKEN},
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        return None, f"备用行情端点返回 {exc.response.status_code}"
    except Exception:
        return None, "备用行情端点请求失败"

    payload_data = payload.get("data") if isinstance(payload, dict) else None
    rows = payload_data.get("diff") if isinstance(payload_data, dict) else []
    if not isinstance(rows, list):
        rows = []
    if not rows:
        return None, f"{secid} 备用行情端点暂无数据"

    expected_market, _, expected_code = secid.partition(".")
    data = next(
        (
            item
            for item in rows
            if isinstance(item, dict)
            and str(item.get("f13") or "") == expected_market
            and str(item.get("f12") or "").upper() == expected_code.upper()
        ),
        rows[0],
    )
    if not isinstance(data, dict) or not data.get("f12"):
        return None, f"{secid} 备用行情端点暂无数据"

    decimals = _int_number(data.get("f152")) or _int_number(data.get("f1")) or 2
    code = str(data.get("f12") or expected_code)
    name = str(data.get("f14") or code)
    market_code = _int_number(data.get("f13"))
    market_label, market_region, currency = _market_label(market_code, code)
    latest = _scale(data.get("f2"), decimals)
    previous_close = _scale(data.get("f18"), decimals)

    card = {
        "kind": "quote",
        "asset_type": _asset_type(code, market_code, name),
        "symbol": code,
        "name": name,
        "market": market_label,
        "market_region": market_region,
        "currency": currency,
        "latest": latest,
        "change": _scale(data.get("f4"), decimals),
        "change_percent": _scale(data.get("f3"), 2),
        "open": _scale(data.get("f17"), decimals),
        "high": _scale(data.get("f15"), decimals),
        "low": _scale(data.get("f16"), decimals),
        "previous_close": previous_close,
        "amplitude_percent": _scale(data.get("f7"), 2),
        "turnover_rate_percent": _scale(data.get("f8"), 2),
        "volume": _plain_number(data.get("f5")),
        "amount": _plain_number(data.get("f6")),
        "market_cap": _plain_number(data.get("f20")),
        "float_market_cap": _plain_number(data.get("f21")),
        "updated_at": _format_timestamp(data.get("f124")),
        "source": "东方财富公开行情",
        "provider": "eastmoney",
        "source_url": f"{EASTMONEY_ULIST_URL}?secids={secid}",
    }
    if latest is None and previous_close is not None:
        card["status"] = "可能停牌或未开盘"
    return _attach_intraday_chart(card, secid, client), None


def _query_eastmoney(symbol: str, market: str, client: httpx.Client) -> tuple[dict[str, Any] | None, str | None]:
    candidates = _eastmoney_candidates(symbol, market)
    if not candidates:
        return None, "未识别出可查询的股票、指数或交易所代码"

    last_error = "未返回行情数据"
    for secid, _label in candidates:
        stock_error: str | None = None
        try:
            response = client.get(EASTMONEY_URL, params={"secid": secid, "fields": EASTMONEY_FIELDS})
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as exc:
            stock_error = f"行情端点返回 {exc.response.status_code}"
        except Exception:
            stock_error = "行情端点请求失败"

        if stock_error:
            fallback_card, fallback_error = _query_eastmoney_ulist(secid, client)
            if fallback_card:
                return fallback_card, None
            trends_card, trends_error = _query_eastmoney_trends_quote(secid, client)
            if trends_card:
                return trends_card, None
            last_error = "；".join(item for item in [stock_error, fallback_error, trends_error] if item)
            continue

        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict) or not data.get("f57"):
            fallback_card, fallback_error = _query_eastmoney_ulist(secid, client)
            if fallback_card:
                return fallback_card, None
            trends_card, trends_error = _query_eastmoney_trends_quote(secid, client)
            if trends_card:
                return trends_card, None
            last_error = fallback_error or trends_error or f"{secid} 暂无数据"
            continue

        decimals = int(data.get("f59") or 2)
        code = str(data.get("f57") or symbol)
        name = str(data.get("f58") or code)
        market_code = int(data["f107"]) if data.get("f107") is not None else None
        market_label, market_region, currency = _market_label(market_code, code)
        latest = _scale(data.get("f43"), decimals)
        previous_close = _scale(data.get("f60"), decimals)
        change = _scale(data.get("f169"), decimals)
        change_percent = _scale(data.get("f170"), 2)

        card = {
            "kind": "quote",
            "asset_type": _asset_type(code, market_code, name),
            "symbol": code,
            "name": name,
            "market": market_label,
            "market_region": market_region,
            "currency": currency,
            "latest": latest,
            "change": change,
            "change_percent": change_percent,
            "open": _scale(data.get("f46"), decimals),
            "high": _scale(data.get("f44"), decimals),
            "low": _scale(data.get("f45"), decimals),
            "previous_close": previous_close,
            "amplitude_percent": _scale(data.get("f171"), 2),
            "turnover_rate_percent": _scale(data.get("f168"), 2),
            "volume": _plain_number(data.get("f47")),
            "amount": _plain_number(data.get("f48")),
            "market_cap": _plain_number(data.get("f116")),
            "float_market_cap": _plain_number(data.get("f117")),
            "updated_at": _format_timestamp(data.get("f86")),
            "source": "东方财富公开行情",
            "provider": "eastmoney",
            "source_url": f"{EASTMONEY_URL}?secid={secid}",
        }
        if latest is None and previous_close is not None:
            card["status"] = "可能停牌或未开盘"
        return _attach_intraday_chart(card, secid, client), None

    return None, last_error


def _parse_fund_response(text: str) -> dict[str, Any] | None:
    match = re.search(r"jsonpgz\((\{.*\})\);?", text.strip())
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _query_fund(symbol: str, client: httpx.Client) -> tuple[dict[str, Any] | None, str | None]:
    code = _normalize_symbol(symbol)
    if not re.fullmatch(r"\d{6}", code):
        return None, "基金代码应为 6 位数字"
    try:
        response = client.get(FUND_URL_TEMPLATE.format(code=code), params={"rt": int(datetime.now().timestamp() * 1000)})
        response.raise_for_status()
    except Exception as exc:
        return None, str(exc)

    data = _parse_fund_response(response.text)
    if not data:
        return None, "天天基金未返回估值数据"

    latest = _plain_number(data.get("gsz"))
    previous_nav = _plain_number(data.get("dwjz"))
    change_percent = _plain_number(data.get("gszzl"))
    change = round(latest - previous_nav, 4) if latest is not None and previous_nav is not None else None
    card = {
        "kind": "quote",
        "asset_type": "开放式基金",
        "symbol": data.get("fundcode") or code,
        "name": data.get("name") or code,
        "market": "场外基金",
        "market_region": "CN",
        "currency": "CNY",
        "latest": latest,
        "change": change,
        "change_percent": change_percent,
        "previous_close": previous_nav,
        "nav_date": data.get("jzrq") or "",
        "updated_at": data.get("gztime") or "",
        "source": "天天基金实时估值",
        "provider": "fundgz",
        "source_url": FUND_URL_TEMPLATE.format(code=code),
    }
    return card, None


def _format_amount(value: Any) -> str:
    number = _plain_number(value)
    if number is None:
        return "--"
    if abs(number) >= 100000000:
        return f"{number / 100000000:.2f} 亿"
    if abs(number) >= 10000:
        return f"{number / 10000:.2f} 万"
    return f"{number:.0f}"


def _format_price(value: Any) -> str:
    number = _plain_number(value)
    if number is None:
        return "--"
    return f"{number:.4f}".rstrip("0").rstrip(".")


def _format_percent(value: Any) -> str:
    number = _plain_number(value)
    if number is None:
        return "--"
    return f"{number:+.2f}%"


def _build_robot_text(cards: list[dict[str, Any]], failures: list[dict[str, str]]) -> str:
    lines = []
    for card in cards:
        lines.append(
            (
                f"{card['name']}({card['symbol']}) 最新 {_format_price(card.get('latest'))} {card.get('currency', '')}，"
                f"涨跌幅 {_format_percent(card.get('change_percent'))}，涨跌额 {_format_price(card.get('change'))}，"
                f"更新时间 {card.get('updated_at') or '--'}。数据源：{card.get('source', '公开行情')}。"
            )
        )
    for failure in failures:
        lines.append(f"{failure['symbol']} 查询失败：{failure['message']}")
    return "\n".join(lines)


def _lookup_symbol(symbol: str, market: str, client: httpx.Client) -> tuple[dict[str, Any] | None, str | None]:
    searched, search_error = _search_full_name(symbol, market, client)
    if searched:
        quote_id = searched["quote_id"]
        if quote_id.startswith("150."):
            return _query_fund(searched["code"], client)
        return _query_eastmoney(quote_id, "secid", client)
    if search_error:
        return None, search_error

    if market == "fund" or (market == "auto" and _is_fund_like_code(_normalize_symbol(symbol))):
        fund_card, fund_error = _query_fund(symbol, client)
        if fund_card or market == "fund":
            return fund_card, fund_error

    if market in {"auto", "cn", "hk", "us", "secid"}:
        quote_card, quote_error = _query_eastmoney(symbol, market, client)
        if quote_card or market != "auto":
            return quote_card, quote_error
        # auto 模式下东方财富没查到：仅当代码形似场外基金时才回退查天天基金，
        # 否则（如指数/股票代码 399997）直接返回东方财富的错误，避免误导性的基金 404
        if not _is_fund_like_code(_normalize_symbol(symbol)):
            return None, quote_error

    fund_card, fund_error = _query_fund(symbol, client)
    return fund_card, fund_error


def run(text: str, market: str = "auto", **_: dict) -> str:
    symbols = _split_symbols(text)
    if not symbols:
        raise AppException(message="请输入股票、指数、基金代码或完整名称", code=4001, status_code=400)
    if len(symbols) > MAX_SYMBOLS:
        raise AppException(message=f"一次最多查询 {MAX_SYMBOLS} 个代码", code=4001, status_code=400)

    market = market if market in {"auto", "cn", "hk", "us", "fund", "secid"} else "auto"
    cards: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    with httpx.Client(timeout=8, headers=DEFAULT_HEADERS, follow_redirects=True, trust_env=False) as client:
        for symbol in symbols:
            card, error = _lookup_symbol(symbol, market, client)
            if card:
                cards.append(card)
            else:
                failures.append({"symbol": symbol, "message": error or "未查询到行情"})

    if not cards:
        message = "；".join(f"{item['symbol']}：{item['message']}" for item in failures) or "未查询到行情"
        raise AppException(message=message, code=4001, status_code=400)

    payload = {
        "query": text,
        "market": market,
        "cards": cards,
        "failures": failures,
        "robot_text": _build_robot_text(cards, failures),
        "json": cards,
        "notes": [
            "行情来自免费公开端点，稳定性和实时性取决于第三方服务。",
            "结果仅用于信息展示和调试，不构成投资建议。",
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
