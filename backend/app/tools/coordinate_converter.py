import json
import math

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "coordinate-converter",
    "name": "拾取坐标/坐标转换",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


PI = math.pi
A = 6378245.0
EE = 0.00669342162296594323


def _transform_lat(lng: float, lat: float) -> float:
    value = (
        -100.0
        + 2.0 * lng
        + 3.0 * lat
        + 0.2 * lat * lat
        + 0.1 * lng * lat
        + 0.2 * math.sqrt(abs(lng))
    )
    value += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    value += (20.0 * math.sin(lat * PI) + 40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    value += (160.0 * math.sin(lat / 12.0 * PI) + 320.0 * math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return value


def _transform_lng(lng: float, lat: float) -> float:
    value = (
        300.0
        + lng
        + 2.0 * lat
        + 0.1 * lng * lng
        + 0.1 * lng * lat
        + 0.1 * math.sqrt(abs(lng))
    )
    value += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    value += (20.0 * math.sin(lng * PI) + 40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    value += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 * math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return value


def _out_of_china(lng: float, lat: float) -> bool:
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def _wgs84_to_gcj02(lng: float, lat: float) -> tuple[float, float]:
    if _out_of_china(lng, lat):
        return lng, lat
    delta_lat = _transform_lat(lng - 105.0, lat - 35.0)
    delta_lng = _transform_lng(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * PI
    magic = math.sin(rad_lat)
    magic = 1 - EE * magic * magic
    sqrt_magic = math.sqrt(magic)
    delta_lat = (delta_lat * 180.0) / (((A * (1 - EE)) / (magic * sqrt_magic)) * PI)
    delta_lng = (delta_lng * 180.0) / ((A / sqrt_magic) * math.cos(rad_lat) * PI)
    return lng + delta_lng, lat + delta_lat


def _gcj02_to_wgs84(lng: float, lat: float) -> tuple[float, float]:
    if _out_of_china(lng, lat):
        return lng, lat
    gcj_lng, gcj_lat = _wgs84_to_gcj02(lng, lat)
    return lng * 2 - gcj_lng, lat * 2 - gcj_lat


def _gcj02_to_bd09(lng: float, lat: float) -> tuple[float, float]:
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * PI * 3000.0 / 180.0)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * PI * 3000.0 / 180.0)
    return z * math.cos(theta) + 0.0065, z * math.sin(theta) + 0.006


def _bd09_to_gcj02(lng: float, lat: float) -> tuple[float, float]:
    x = lng - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * PI * 3000.0 / 180.0)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * PI * 3000.0 / 180.0)
    return z * math.cos(theta), z * math.sin(theta)


def _parse_point(text: str) -> tuple[float, float]:
    normalized = text.replace("，", ",").replace("\n", ",").replace("\t", ",").strip()
    parts = [item.strip() for item in normalized.split(",") if item.strip()]
    if len(parts) == 1:
        parts = [item for item in parts[0].split() if item]
    if len(parts) != 2:
        raise AppException(message="请输入经纬度，格式如 116.404,39.915", code=4001, status_code=400)
    try:
        lng = float(parts[0])
        lat = float(parts[1])
    except ValueError as exc:
        raise AppException(message="经纬度必须是数字", code=4001, status_code=400) from exc
    return lng, lat


def _convert(lng: float, lat: float, from_system: str, to_system: str) -> tuple[float, float]:
    if from_system == to_system:
        return lng, lat

    if from_system == "wgs84" and to_system == "gcj02":
        return _wgs84_to_gcj02(lng, lat)
    if from_system == "gcj02" and to_system == "wgs84":
        return _gcj02_to_wgs84(lng, lat)
    if from_system == "gcj02" and to_system == "bd09":
        return _gcj02_to_bd09(lng, lat)
    if from_system == "bd09" and to_system == "gcj02":
        return _bd09_to_gcj02(lng, lat)
    if from_system == "wgs84" and to_system == "bd09":
        return _gcj02_to_bd09(*_wgs84_to_gcj02(lng, lat))
    if from_system == "bd09" and to_system == "wgs84":
        return _gcj02_to_wgs84(*_bd09_to_gcj02(lng, lat))

    raise AppException(message="暂不支持所选坐标系转换", code=4001, status_code=400)


def run(
    text: str,
    from_system: str = "wgs84",
    to_system: str = "gcj02",
    precision: int = 6,
    **_: dict,
) -> str:
    if from_system not in {"wgs84", "gcj02", "bd09"} or to_system not in {"wgs84", "gcj02", "bd09"}:
        raise AppException(message="坐标系必须是 wgs84、gcj02 或 bd09", code=4001, status_code=400)

    try:
        precision = int(precision)
    except (TypeError, ValueError) as exc:
        raise AppException(message="精度必须是整数", code=4001, status_code=400) from exc

    if precision < 0 or precision > 10:
        raise AppException(message="精度必须在 0 到 10 之间", code=4001, status_code=400)

    lng, lat = _parse_point(text)
    output_lng, output_lat = _convert(lng, lat, from_system, to_system)
    payload = {
        "from_system": from_system,
        "to_system": to_system,
        "input": {
            "lng": round(lng, precision),
            "lat": round(lat, precision),
        },
        "output": {
            "lng": round(output_lng, precision),
            "lat": round(output_lat, precision),
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
