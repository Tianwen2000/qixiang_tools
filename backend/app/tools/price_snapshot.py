import csv
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime
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
SINA_HQ_URL = "https://hq.sinajs.cn/list="
FRANKFURTER_URL = "https://api.frankfurter.app/latest"
MOA_LIST_URL = "https://scs.moa.gov.cn/jcyj/"
MYSTEEL_MOBILE_URL = "https://gc.m.mysteel.com/"
STOOQ_URL = "https://stooq.com/q/l/"


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


def run_domestic_oil(text: str = "", **_: dict) -> str:
    region = (text or "北京").strip().replace("省", "").replace("市", "")
    payload = _request_json(XXAPI_OIL_URL)
    rows = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise AppException(message="油价接口未返回有效数据", code=5001, status_code=502)

    target = None
    for item in rows:
        name = str(item.get("regionName") or "")
        if region in name or name.replace("省", "").replace("市", "") == region:
            target = item
            break
    if target is None:
        target = rows[0] if rows else None
    if not isinstance(target, dict):
        raise AppException(message="未查询到油价数据", code=4001, status_code=400)

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
        "XXAPI 今日油价公开接口",
        str(target.get("date") or ""),
        ["输入省份可切换地区，例如：广东、上海、四川。"],
    )


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
    base = (text or "USD").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", base):
        raise AppException(message="请输入 3 位货币代码，例如 USD、CNY、EUR", code=4001, status_code=400)
    targets = ["CNY", "USD", "EUR", "JPY", "GBP", "HKD"]
    targets = [item for item in targets if item != base]
    payload = _request_json(FRANKFURTER_URL, params={"from": base, "to": ",".join(targets)})
    rates = payload.get("rates") if isinstance(payload, dict) else None
    if not isinstance(rates, dict):
        raise AppException(message="汇率接口未返回有效数据", code=5001, status_code=502)
    rows = [(f"{base}/{code}", value, "") for code, value in rates.items()]
    return _format_snapshot(f"今日汇率 - 1 {base}", rows, "Frankfurter 汇率公开接口", str(payload.get("date") or ""))


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
    return _format_snapshot("今日股票指数", rows, "东方财富/新浪公开行情聚合", updated, notes)


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
    lines = [
        "# 今日钢材/水泥/建材价格",
        f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"数据源：我的钢铁移动行情页：{MYSTEEL_MOBILE_URL}",
        "",
    ]
    lines.extend(f"- {title}" for title in unique_titles)
    lines.append("")
    lines.append("备注：该工具展示公开页面行情摘要，不等同于指定城市/规格的成交价。")
    lines.append("提示：免费公开端点稳定性和实时性取决于第三方服务，结果仅用于快速查看。")
    return "\n".join(lines)
