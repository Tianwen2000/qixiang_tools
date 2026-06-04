import re
from pathlib import Path

from PIL import Image

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "image-resizer",
    "name": "图片像素比调整",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}

MAX_DIMENSION = 12000
FORMAT_MAP = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "tif": "TIFF",
    "tiff": "TIFF",
    "gif": "GIF",
}


def _parse_dim(value: str | int | float, label: str) -> int:
    raw = str(value).strip()
    if not raw:
        raise AppException(message=f"请输入{label}", code=4001, status_code=400)
    try:
        number = int(round(float(raw)))
    except (TypeError, ValueError) as exc:
        raise AppException(message=f"{label}需为数字，例如 750", code=4001, status_code=400) from exc
    if number < 1 or number > MAX_DIMENSION:
        raise AppException(message=f"{label}需在 1~{MAX_DIMENSION} 像素之间", code=4001, status_code=400)
    return number


def _parse_ratio(value: str) -> tuple[float, float]:
    raw = str(value).strip().replace("：", ":")
    matched = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*[:xX×*]\s*(\d+(?:\.\d+)?)\s*", raw)
    if not matched:
        raise AppException(message="宽高比格式应为 宽:高，例如 9:16", code=4001, status_code=400)
    rw = float(matched.group(1))
    rh = float(matched.group(2))
    if rw <= 0 or rh <= 0:
        raise AppException(message="宽高比必须为正数", code=4001, status_code=400)
    return rw, rh


def run(
    input_path: str,
    output_dir: str,
    filename: str = "",
    mode: str = "size",
    width: str = "",
    height: str = "",
    ratio: str = "",
    ratio_base: str = "width",
    **_: dict,
) -> str:
    """自由调整图片像素尺寸或宽高比，直接拉伸重采样（允许变形），不保持原比例。"""
    suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"

    try:
        image = Image.open(input_path)
        image.load()
    except Exception as exc:
        raise AppException(message=f"无法读取图片：{exc}", code=4001, status_code=400) from exc

    orig_w, orig_h = image.size
    if mode == "ratio":
        rw, rh = _parse_ratio(ratio)
        if ratio_base == "height":
            new_h = orig_h
            new_w = max(1, round(orig_h * rw / rh))
        else:
            new_w = orig_w
            new_h = max(1, round(orig_w * rh / rw))
    else:
        new_w = _parse_dim(width, "目标宽度")
        new_h = _parse_dim(height, "目标高度")

    if new_w > MAX_DIMENSION or new_h > MAX_DIMENSION:
        raise AppException(message=f"目标尺寸过大，单边上限 {MAX_DIMENSION} 像素", code=4001, status_code=400)

    resized = image.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

    target_format = FORMAT_MAP.get(suffix)
    if target_format is None:
        target_format = "PNG"
        suffix = "png"
    if target_format == "JPEG" and resized.mode not in {"RGB", "L", "CMYK"}:
        resized = resized.convert("RGB")

    target_path = Path(output_dir) / f"resized-{new_w}x{new_h}.{suffix}"
    try:
        resized.save(target_path, format=target_format)
    except Exception as exc:
        raise AppException(message=f"图片保存失败：{exc}", code=5002, status_code=500) from exc
    return str(target_path)
