"""文件说明：实现 price snapshot 工具的后端逻辑。"""

import csv
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any

from app.core.exceptions import AppException


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,text/html,*/*",
}
SINA_HEADERS = {
    **DEFAULT_HEADERS,
    "Referer": "https://finance.sina.com.cn/",
}

XXAPI_OIL_URL = "https://v2.xxapi.cn/api/oilPrice"
XIAOXIONG_OIL_URL = "https://www.xiaoxiongyouhao.com/fprice/"
SINA_HQ_URL = "https://hq.sinajs.cn/list="
FRANKFURTER_URL = "https://api.frankfurter.app/latest"
ER_API_URL = "https://open.er-api.com/v6/latest/"
MOA_LIST_URL = "https://scs.moa.gov.cn/jcyj/"
MYSTEEL_MOBILE_URL = "https://gc.m.mysteel.com/"
MYSTEEL_SAND_STONE_URLS = [
    "https://www.mysteel.com/hot/1163703.html",
    "https://www.mysteel.com/hot/1001046.html",
]
AWHOUSE_MATERIAL_COST_URL = "https://www.awhouse.art/unit-material-cost"
STOOQ_URL = "https://stooq.com/q/l/"

COMMON_RATE_TARGETS = ["CNY", "USD", "EUR", "JPY", "GBP", "HKD"]
CURRENCY_ALIASES = {
    "人民币": "CNY",
    "中国元": "CNY",
    "cny": "CNY",
    "rmb": "CNY",
    "yuan": "CNY",
    "美元": "USD",
    "美金": "USD",
    "usd": "USD",
    "dollar": "USD",
    "dollars": "USD",
    "us dollar": "USD",
    "欧元": "EUR",
    "eur": "EUR",
    "euro": "EUR",
    "euros": "EUR",
    "日元": "JPY",
    "日币": "JPY",
    "jpy": "JPY",
    "yen": "JPY",
    "英镑": "GBP",
    "gbp": "GBP",
    "pound": "GBP",
    "pounds": "GBP",
    "pound sterling": "GBP",
    "港币": "HKD",
    "港元": "HKD",
    "hkd": "HKD",
    "hong kong dollar": "HKD",
    "澳元": "AUD",
    "澳币": "AUD",
    "aud": "AUD",
    "australian dollar": "AUD",
    "加元": "CAD",
    "加币": "CAD",
    "cad": "CAD",
    "canadian dollar": "CAD",
    "瑞士法郎": "CHF",
    "chf": "CHF",
    "swiss franc": "CHF",
    "新加坡元": "SGD",
    "新币": "SGD",
    "sgd": "SGD",
    "singapore dollar": "SGD",
    "韩元": "KRW",
    "krw": "KRW",
    "won": "KRW",
}


def _request_text(url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None, encoding: str = "utf-8") -> str:
    full_url = url
    if params:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(full_url, headers=headers or DEFAULT_HEADERS)
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.read().decode(encoding, errors="replace")


def _request_json(url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
    return json.loads(_request_text(url, params=params, headers=headers))


def _plain_number(value: Any) -> float | None:
    if value in {None, "", "-", "N/D"}:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _fmt_number(value: Any, digits: int = 4) -> str:
    number = _plain_number(value)
    if number is None:
        return "--"
    return f"{number:.{digits}f}".rstrip("0").rstrip(".")


def _fmt_amount(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _clean_text(value: str) -> str:
    value = re.sub(r"<script[\s\S]*?</script>", " ", value, flags=re.I)
    value = re.sub(r"<style[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _format_snapshot(title: str, rows: list[tuple[str, Any, str]], source: str, updated_at: str = "", notes: list[str] | None = None) -> str:
    lines = [f"# {title}"]
    if updated_at:
        lines.append(f"更新时间：{updated_at}")
    lines.append(f"数据源：{source}")
    lines.append("")
    max_name_len = max((len(name) for name, _value, _unit in rows), default=4)
    for name, value, unit in rows:
        lines.append(f"- {name.ljust(max_name_len)}  {_fmt_number(value)}{unit}")
    if notes:
        lines.append("")
        lines.extend(f"备注：{note}" for note in notes if note)
    lines.append("")
    lines.append("提示：免费公开端点稳定性和实时性取决于第三方服务，结果仅用于快速查看。")
    return "\n".join(lines)


def _parse_sina_hq(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for symbol, payload in re.findall(r'var hq_str_([^=]+)="(.*?)";', text, flags=re.S):
        if payload:
            result[symbol] = payload.split(",")
    return result


def _fetch_sina(symbols: list[str]) -> dict[str, list[str]]:
    text = _request_text(f"{SINA_HQ_URL}{','.join(symbols)}", headers=SINA_HEADERS, encoding="gbk")
    return _parse_sina_hq(text)


def _fetch_stooq(symbol: str) -> dict[str, str] | None:
    text = _request_text(STOOQ_URL, params={"s": symbol, "f": "sd2t2ohlcv", "h": "", "e": "csv"})
    rows = list(csv.DictReader(text.splitlines()))
    if not rows:
        return None
    row = rows[0]
    if row.get("Close") in {"N/D", None, ""}:
        return None
    return row


def _extract_amount(text: str) -> float:
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text.replace(",", ""))
    if not match:
        return 1.0
    amount = _plain_number(match.group(0))
    return amount if amount and amount > 0 else 1.0


def _extract_currency_codes(text: str) -> list[str]:
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    found: list[tuple[int, int, str]] = []
    lower_text = cleaned.lower()
    for alias, code in sorted(CURRENCY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        alias_lower = alias.lower()
        pattern = re.escape(alias_lower)
        if alias_lower.isascii() and alias_lower.replace(" ", "").isalpha():
            pattern = rf"(?<![a-z]){pattern}(?![a-z])"
        for match in re.finditer(pattern, lower_text):
            found.append((match.start(), match.end(), code))
    for match in re.finditer(r"(?<![A-Za-z])([A-Za-z]{3})(?![A-Za-z])", cleaned):
        found.append((match.start(), match.end(), match.group(1).upper()))
    codes: list[str] = []
    occupied: list[tuple[int, int]] = []
    for start, end, code in sorted(found, key=lambda item: (item[0], -(item[1] - item[0]))):
        if any(start < used_end and end > used_start for used_start, used_end in occupied):
            continue
        occupied.append((start, end))
        if code not in codes:
            codes.append(code)
    return codes


def _normalize_region(value: str) -> str:
    return (value or "").strip().replace("省", "").replace("市", "").replace("自治区", "").replace("特别行政区", "")


def _parse_date_value(value: str) -> datetime | None:
    match = re.search(r"(\d{4})[-年/](\d{1,2})[-月/](\d{1,2})", value or "")
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    try:
        return parsedate_to_datetime(value).replace(tzinfo=None)
    except (TypeError, ValueError):
        return None


def _oil_snapshot_from_target(target: dict[str, Any], region: str, source: str, notes: list[str] | None = None) -> str:
    area = str(target.get("regionName") or region)
    rows_out = [
        ("89号汽油", target.get("n89"), " 元/升"),
        ("92号汽油", target.get("n92"), " 元/升"),
        ("95号汽油", target.get("n95"), " 元/升"),
        ("98号汽油", target.get("n98"), " 元/升"),
        ("0号柴油", target.get("n0"), " 元/升"),
    ]
    return _format_snapshot(
        f"今日油价 - {area}",
        rows_out,
        source,
        str(target.get("date") or ""),
        ["输入省份可切换地区，例如：广东、上海、四川。", *(notes or [])],
    )


def _fetch_xiaoxiong_oil(region: str) -> dict[str, Any]:
    html = _request_text(XIAOXIONG_OIL_URL, headers=DEFAULT_HEADERS)
    date_match = re.search(r"今日油价[（(](\d{4}-\d{1,2}-\d{1,2})[）)]", html)
    updated_at = date_match.group(1) if date_match else ""
    row_pattern = re.compile(
        r'<tr>\s*<td class="region-name">.*?>([^<>]+)</a></td>\s*'
        r'<td[^>]*>([\d.\\-]+)</td>\s*'
        r'<td[^>]*>([\d.\\-]+)</td>\s*'
        r'<td[^>]*>([\d.\\-]+)</td>',
        flags=re.S,
    )
    rows = []
    for name, n92, n95, n0 in row_pattern.findall(html):
        rows.append(
            {
                "regionName": _clean_text(name),
                "n89": None,
                "n92": n92,
                "n95": n95,
                "n98": None,
                "n0": n0,
                "date": updated_at,
            }
        )
    if not rows:
        raise AppException(message="油价兜底页面未解析到有效数据", code=5001, status_code=502)

    normalized = _normalize_region(region)
    for item in rows:
        if normalized and normalized in _normalize_region(str(item.get("regionName") or "")):
            return item
    return rows[0]


def run_domestic_oil(text: str = "", **_: dict) -> str:
    region = _normalize_region(text or "北京")
    primary_target = None
    primary_error: Exception | None = None
    try:
        payload = _request_json(XXAPI_OIL_URL)
        rows = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            raise AppException(message="油价接口未返回有效数据", code=5001, status_code=502)
        for item in rows:
            name = str(item.get("regionName") or "")
            if region in _normalize_region(name) or _normalize_region(name) == region:
                primary_target = item
                break
        if primary_target is None:
            primary_target = rows[0] if rows else None
        if not isinstance(primary_target, dict):
            raise AppException(message="未查询到油价数据", code=4001, status_code=400)
    except Exception as exc:
        primary_error = exc

    try:
        fallback_target = _fetch_xiaoxiong_oil(region)
        primary_date = _parse_date_value(str(primary_target.get("date") if primary_target else ""))
        fallback_date = _parse_date_value(str(fallback_target.get("date") or ""))
        if primary_target is None or (fallback_date and (not primary_date or fallback_date >= primary_date)):
            return _oil_snapshot_from_target(
                fallback_target,
                region,
                "小熊油耗全国油价页（兜底）",
                ["兜底页面暂不提供 89/98 号汽油价格时会显示 --。"],
            )
    except Exception:
        if primary_target is None and primary_error:
            raise primary_error

    if primary_target is None:
        raise AppException(message="未查询到油价数据", code=4001, status_code=400)
    return _oil_snapshot_from_target(primary_target, region, "XXAPI 今日油价公开接口")


def run_international_crude(text: str = "", **_: dict) -> str:
    quotes = _fetch_sina(["hf_CL", "hf_OIL"])
    rows = []
    updated = ""
    for symbol, label in [("hf_CL", "WTI/纽约原油"), ("hf_OIL", "布伦特原油")]:
        parts = quotes.get(symbol) or []
        if len(parts) >= 14:
            rows.append((label, parts[0], " 美元/桶"))
            updated = updated or f"{parts[12]} {parts[6]}"
    if not rows:
        stooq = _fetch_stooq("cl.f")
        if stooq:
            rows.append(("WTI 原油期货", stooq.get("Close"), " 美元/桶"))
            updated = f"{stooq.get('Date')} {stooq.get('Time')}"
    if not rows:
        raise AppException(message="国际原油价格端点暂无可用数据", code=5001, status_code=502)
    return _format_snapshot("今日国际原油价格", rows, "新浪财经外盘期货；备用 Stooq CSV", updated)


def _usd_cny_rate() -> float | None:
    quotes = _fetch_sina(["USDCNY", "fx_susdcny"])
    for symbol in ("USDCNY", "fx_susdcny"):
        parts = quotes.get(symbol) or []
        if len(parts) > 1:
            rate = _plain_number(parts[1])
            if rate:
                return rate
    try:
        payload = _request_json(FRANKFURTER_URL, params={"from": "USD", "to": "CNY"})
        return _plain_number(payload.get("rates", {}).get("CNY"))
    except Exception:
        return None


def _run_precious_metal(title: str, symbol: str, label: str) -> str:
    quotes = _fetch_sina([symbol])
    parts = quotes.get(symbol) or []
    if len(parts) < 14:
        raise AppException(message=f"{title}端点暂无可用数据", code=5001, status_code=502)
    price_usd_oz = _plain_number(parts[0])
    rate = _usd_cny_rate()
    rows: list[tuple[str, Any, str]] = [(label, price_usd_oz, " 美元/盎司")]
    if price_usd_oz and rate:
        rows.append((f"{label}折算", price_usd_oz * rate / 31.1034768, " 元/克"))
    rows.extend(
        [
            ("今日最高", parts[4], " 美元/盎司"),
            ("今日最低", parts[5], " 美元/盎司"),
            ("昨收参考", parts[7], " 美元/盎司"),
        ]
    )
    return _format_snapshot(
        title,
        rows,
        "新浪财经外盘贵金属行情",
        f"{parts[12]} {parts[6]}",
        ["人民币/克为按 USD/CNY 粗略折算，非金店零售价。"],
    )


def run_gold(text: str = "", **_: dict) -> str:
    _ = text
    return _run_precious_metal("今日金价", "hf_GC", "纽约黄金")


def run_silver(text: str = "", **_: dict) -> str:
    _ = text
    return _run_precious_metal("今日白银价格", "hf_SI", "纽约白银")


def run_exchange_rate(text: str = "", **_: dict) -> str:
    raw_text = (text or "").strip()
    codes = _extract_currency_codes(raw_text)
    if raw_text and not codes:
        raise AppException(message="请输入货币代码或中文币种，例如 USD、美元、100美元兑人民币", code=4001, status_code=400)

    amount = _extract_amount(raw_text)
    base = codes[0] if codes else "USD"
    targets = [codes[1]] if len(codes) >= 2 else COMMON_RATE_TARGETS
    targets = [item for item in targets if item != base]
    if not targets:
        raise AppException(message="换算币种不能和基准币种相同", code=4001, status_code=400)

    payload: dict[str, Any] = {}
    rates: dict[str, Any] | None = None
    source = "Frankfurter 汇率公开接口"
    primary_error: Exception | None = None
    try:
        payload = _request_json(FRANKFURTER_URL, params={"from": base, "to": ",".join(targets)})
        rates = payload.get("rates") if isinstance(payload, dict) else None
        if not isinstance(rates, dict):
            raise AppException(message="汇率接口未返回有效数据", code=5001, status_code=502)
    except Exception as exc:
        primary_error = exc

    try:
        fallback_payload = _request_json(f"{ER_API_URL}{base}")
        fallback_rates_raw = fallback_payload.get("rates") if isinstance(fallback_payload, dict) else None
        if not isinstance(fallback_rates_raw, dict):
            raise AppException(message="汇率兜底接口未返回有效数据", code=5001, status_code=502)
        fallback_rates = {code: fallback_rates_raw.get(code) for code in targets if code in fallback_rates_raw}
        if len(fallback_rates) == len(targets):
            fallback_date = str(fallback_payload.get("time_last_update_utc") or fallback_payload.get("time_last_update_iso") or "")
            primary_date = _parse_date_value(str(payload.get("date") or ""))
            fallback_date_value = _parse_date_value(fallback_date)
            if rates is None or (fallback_date_value and (not primary_date or fallback_date_value >= primary_date)):
                payload = {"date": fallback_date}
                rates = fallback_rates
                source = "ExchangeRate-API 免费公开接口（兜底）"
    except Exception:
        if rates is None and primary_error:
            raise primary_error

    if not isinstance(rates, dict):
        raise AppException(message="汇率接口未返回有效数据", code=5001, status_code=502)

    if amount != 1 or len(rates) == 1:
        rows = [(f"{_fmt_amount(amount)} {base} -> {code}", amount * value, f" {code}") for code, value in rates.items()]
        title = f"今日汇率换算 - {_fmt_amount(amount)} {base}"
    else:
        rows = [(f"{base}/{code}", value, "") for code, value in rates.items()]
        title = f"今日汇率 - 1 {base}"
    return _format_snapshot(title, rows, source, str(payload.get("date") or ""))


def _latest_moa_article() -> tuple[str, str]:
    html = _request_text(MOA_LIST_URL, headers=DEFAULT_HEADERS)
    matches = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, flags=re.S)
    for href, raw_text in matches:
        title = _clean_text(raw_text)
        if "农产品批发价格200指数" in title:
            return urllib.parse.urljoin(MOA_LIST_URL, href), title
    raise AppException(message="农业农村部监测预警列表暂无价格文章", code=5001, status_code=502)


def run_food_price(text: str = "", **_: dict) -> str:
    _ = text
    url, title = _latest_moa_article()
    article = _clean_text(_request_text(url, headers=DEFAULT_HEADERS))
    patterns = [
        ("猪肉", r"猪肉平均价格为([\d.]+)元/公斤，([^；。]+)"),
        ("鸡蛋", r"鸡蛋([\d.]+)元/公斤，([^；。]+)"),
        ("白条鸡", r"白条鸡([\d.]+)元/公斤，([^；。]+)"),
        ("28种蔬菜", r"28种蔬菜平均价格为([\d.]+)元/公斤，([^；。]+)"),
    ]
    rows = []
    notes = []
    for name, pattern in patterns:
        match = re.search(pattern, article)
        if match:
            rows.append((name, match.group(1), " 元/公斤"))
            notes.append(f"{name}：{match.group(2)}")
    if not rows:
        raise AppException(message="未能解析农产品价格正文", code=5001, status_code=502)
    date_match = re.search(r"(\d+月\d+日)", title)
    return _format_snapshot("今日猪肉/鸡蛋/蔬菜价格", rows, f"农业农村部市场与信息化司：{url}", date_match.group(1) if date_match else "", notes)


def run_stock_index(text: str = "", **_: dict) -> str:
    from app.tools import market_quote

    query = (text or "1.000001 0.399001 0.399006 1.000300 1.000905").strip()
    result = json.loads(market_quote.run(query, market="auto"))
    cards = result.get("cards") or []
    rows = []
    notes = []
    for card in cards:
        name = f"{card.get('name')}({card.get('symbol')})"
        rows.append((name, card.get("latest"), ""))
        change_percent = card.get("change_percent")
        if change_percent is not None:
            notes.append(f"{name} 涨跌幅：{_fmt_number(change_percent, 2)}%")
    if not rows:
        raise AppException(message="未查询到股票指数", code=4001, status_code=400)
    updated = next((str(card.get("updated_at")) for card in cards if card.get("updated_at")), "")
    sources = "；".join(dict.fromkeys(str(card.get("source")) for card in cards if card.get("source")))
    return _format_snapshot("今日股票指数", rows, sources or "公开行情聚合", updated, notes)


def run_building_materials(text: str = "", **_: dict) -> str:
    _ = text
    try:
        html = _request_text(MYSTEEL_MOBILE_URL, headers=DEFAULT_HEADERS)
    except Exception as exc:
        raise AppException(message=f"建材行情页请求失败：{exc}", code=5001, status_code=502) from exc
    links = re.findall(r'<a[^>]+href="[^"]+"[^>]*>(.*?)</a>', html, flags=re.S)
    titles = []
    for raw_link in links:
        title = _clean_text(raw_link)
        if re.search(r"(建筑钢材|水泥|钢材|建材).*(价格|行情)|水泥价格", title):
            titles.append(title)
    unique_titles: list[str] = []
    for title in titles:
        if title not in unique_titles:
            unique_titles.append(title)
        if len(unique_titles) >= 8:
            break
    if not unique_titles:
        unique_titles = ["当前公开页面未解析到具体价格条目，可稍后重试。"]
    sand_stone_titles: list[str] = []
    for url in MYSTEEL_SAND_STONE_URLS:
        try:
            sand_html = _request_text(url, headers=DEFAULT_HEADERS)
        except Exception:
            continue
        candidates = re.findall(r"<li[^>]*>(.*?)</li>", sand_html, flags=re.S)
        candidates.extend(re.findall(r'<a[^>]+href="[^"]+"[^>]*>(.*?)</a>', sand_html, flags=re.S))
        for raw_item in candidates:
            title = _clean_text(raw_item)
            if len(title) > 120 or "当前位置" in title:
                continue
            if re.search(r"(红砖|砂石|河砂|机制砂|碎石|石粉).*(价格|行情|报价)", title):
                sand_stone_titles.append(title)
    unique_sand_stone_titles: list[str] = []
    for title in sand_stone_titles:
        if title not in unique_sand_stone_titles:
            unique_sand_stone_titles.append(title)
        if len(unique_sand_stone_titles) >= 6:
            break

    reference_rows = [
        ("红砖", "0.6-0.8 元/块"),
        ("砂石", "100-200 元/m³"),
        ("碎石/石子", "通常随地区、粒径和运输距离浮动，建议按当地砂石行情核价"),
    ]
    lines = [
        "# 今日钢材/水泥/建材价格",
        f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"数据源：我的钢铁移动行情页：{MYSTEEL_MOBILE_URL}",
        "",
        "## 钢材/水泥/建材行情摘要",
    ]
    lines.extend(f"- {title}" for title in unique_titles)
    if unique_sand_stone_titles:
        lines.append("")
        lines.append("## 砂石/石材行情摘要")
        lines.extend(f"- {title}" for title in unique_sand_stone_titles)
    lines.append("")
    lines.append("## 红砖/砂石/石子参考价")
    lines.extend(f"- {name}：{value}" for name, value in reference_rows)
    lines.append("")
    lines.append(f"参考价来源：AWhouse 建材计价信息汇总：{AWHOUSE_MATERIAL_COST_URL}")
    lines.append("备注：该工具展示公开页面行情摘要，不等同于指定城市/规格的成交价。")
    lines.append("备注：红砖、砂石、石子为常用参考价区间或核价提示，非今日实时成交价。")
    lines.append("提示：免费公开端点稳定性和实时性取决于第三方服务，结果仅用于快速查看。")
    return "\n".join(lines)
