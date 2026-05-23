import ipaddress
import re
import socket
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import httpx


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "close",
}

SERVICES = {
    "Baidu (百度)": {
        "url": "https://www.baidu.com/s?wd=ip",
        "method": "baidu",
    },
    "Aliyun (阿里)": {
        "url": "https://ip.sml2.com/",
        "method": "text",
    },
    "ipinfo.io": {
        "url": "https://ipinfo.io/ip",
        "method": "text",
    },
    "ipify": {
        "url": "https://api.ipify.org",
        "method": "text",
    },
    "ipecho.net": {
        "url": "https://ipecho.net/plain",
        "method": "text",
    },
}

SPECIAL_SERVICES = {
    "Domestic Real IP": {
        "urls": [
            "http://myip.ipip.net",
            "https://myip.ipip.net",
            "https://myip.la",
        ],
        "method": "ipip",
    },
    "Overseas IP": {
        "urls": [
            "https://ifconfig.me/ip",
            "http://ifconfig.me/ip",
        ],
        "method": "text",
    },
}


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def is_valid_ip(ip_value: str) -> bool:
    try:
        ipaddress.ip_address(ip_value.strip())
        return True
    except Exception:
        return False


def extract_ip_from_text(text: str) -> str | None:
    stripped = text.strip()
    ipv4_candidates = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", stripped)
    for candidate in ipv4_candidates:
        try:
            ipaddress.IPv4Address(candidate)
            return candidate
        except Exception:
            continue

    parts = re.split(r"[\s,;，；]+", stripped)
    for part in parts:
        candidate = part.strip("[]()<>，。:：")
        if is_valid_ip(candidate):
            return candidate
    return None


def extract_ip_baidu(html: str) -> str | None:
    return extract_ip_from_text(html)


def extract_ip_ipip(text: str) -> str | None:
    return extract_ip_from_text(text)


def get_ip_from_service(name: str, config: dict[str, Any]) -> dict[str, Any]:
    urls = config.get("urls") or [config["url"]]
    method = config["method"]

    for url in urls:
        try:
            with httpx.Client(
                timeout=6,
                headers=DEFAULT_HEADERS,
                follow_redirects=True,
                trust_env=False,
            ) as client:
                response = client.get(url)
            text = response.text.strip()

            if method == "baidu":
                ip_value = extract_ip_baidu(text)
            elif method == "ipip":
                ip_value = extract_ip_ipip(text)
            else:
                ip_value = extract_ip_from_text(text)

            if ip_value and is_valid_ip(ip_value):
                return {
                    "service": name,
                    "ip": ip_value,
                    "ok": True,
                    "raw": text[:200],
                    "url": url,
                }
        except Exception:
            continue

    return {
        "service": name,
        "ip": "请求失败或未返回有效IP",
        "ok": False,
        "raw": "",
        "url": "",
    }


def analyze_split_ip(domestic_ip: str, overseas_ip: str) -> dict[str, str]:
    if not domestic_ip or not is_valid_ip(domestic_ip):
        return {
            "status": "unknown",
            "message": "无法获取国内真实 IP，不能准确判断是否存在分流。",
        }

    if not overseas_ip or not is_valid_ip(overseas_ip):
        return {
            "status": "unknown",
            "message": "无法获取境外视角 IP，不能准确判断是否存在分流。",
        }

    if domestic_ip == overseas_ip:
        return {
            "status": "same",
            "message": "国内真实 IP 与境外视角 IP 一致，当前大概率没有分流，或国内外请求走的是同一出口。",
        }

    return {
        "status": "split",
        "message": "国内真实 IP 与境外视角 IP 不一致，当前大概率存在分流 / VPN / 代理 / 多出口网络。",
    }


def query_group(services: dict[str, dict[str, Any]], max_workers: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(get_ip_from_service, name, config): name
            for name, config in services.items()
        }
        for future in as_completed(future_map):
            results.append(future.result())
    return sorted(results, key=lambda item: list(services).index(item["service"]))


def build_public_summary(results: list[dict[str, Any]], domestic_ip: str, overseas_ip: str) -> dict[str, Any]:
    valid_ips = [item["ip"] for item in results if item.get("ok") and is_valid_ip(item.get("ip", ""))]
    if not valid_ips:
        return {
            "status": "failed",
            "majority_ip": "",
            "message": "所有公共服务均未返回有效公网 IP，请检查网络。",
            "votes": [],
        }

    counts = Counter(valid_ips)
    majority_ip, frequency = counts.most_common(1)[0]
    votes = [{"ip": ip_value, "count": count} for ip_value, count in counts.most_common()]

    if len(counts) == 1:
        status = "same"
        message = "所有公网服务结果一致。"
    else:
        status = "different"
        message = "公网 IP 结果不一致，可能存在 CDN / 代理 / DNS 差异 / 分流。"

    if is_valid_ip(domestic_ip) and majority_ip == domestic_ip:
        relation = "多数公网服务更接近国内真实 IP。"
    elif is_valid_ip(overseas_ip) and majority_ip == overseas_ip:
        relation = "多数公网服务更接近境外出口 IP。"
    else:
        relation = "多数公网服务与国内/境外专用检测结果都不完全一致，网络出口可能较复杂。"

    return {
        "status": status,
        "majority_ip": majority_ip,
        "frequency": frequency,
        "message": message,
        "relation": relation,
        "votes": votes,
    }


def run(text: str = "", **_: Any) -> dict[str, Any]:
    _ = text
    local_ip = get_local_ip()
    special_results = query_group(SPECIAL_SERVICES, max_workers=2)
    special_by_service = {item["service"]: item for item in special_results}
    domestic = special_by_service.get("Domestic Real IP", {})
    overseas = special_by_service.get("Overseas IP", {})
    domestic_ip = domestic.get("ip", "")
    overseas_ip = overseas.get("ip", "")
    split_result = analyze_split_ip(domestic_ip, overseas_ip)

    public_results = query_group(SERVICES, max_workers=6)
    public_summary = build_public_summary(public_results, domestic_ip, overseas_ip)

    return {
        "local_ip": local_ip,
        "domestic": domestic,
        "overseas": overseas,
        "split_result": split_result,
        "public_results": public_results,
        "public_summary": public_summary,
        "notes": [
            "myip.ipip.net 更适合看国内视角下的真实出口 IP。",
            "ifconfig.me 更适合看境外服务看到的出口 IP。",
            "如果国内与境外结果不一致，通常说明存在 VPN、策略路由、代理或不同站点走不同出口。",
            "百度等页面型服务可能受 CDN、缓存、反爬影响，仅供参考。",
        ],
    }
