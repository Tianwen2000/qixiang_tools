import io
from pathlib import Path

from PIL import Image

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.utils.image_utils import IMAGE_FORMATS, image_extension_from_format, load_image, save_image


TOOL_META = {
    "slug": "image-compressor",
    "name": "图片压缩",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}

HEIF_SUFFIXES = {"heic", "heif"}
RESIZE_FACTORS = {2, 3, 4, 10}


def _register_heif_support() -> None:
    try:
        from pillow_heif import register_heif_opener
    except Exception as exc:  # pragma: no cover - dependency safety net
        raise AppException(message=f"当前环境暂不支持 HEIC/HEIF 压缩：{exc}", code=5002, status_code=500) from exc
    register_heif_opener()


def _parse_target_bytes(value: str | int | float, current_bytes: int | None = None) -> int:
    raw = str(value).strip().lower().replace(" ", "")
    if not raw:
        raise AppException(message="请输入目标大小", code=4001, status_code=400)

    if raw.endswith("%"):
        if current_bytes is None:
            raise AppException(message="百分比目标需要基于当前文件大小计算", code=4001, status_code=400)
        try:
            percent = float(raw[:-1])
        except ValueError as exc:
            raise AppException(message="目标大小百分比格式无效，例如 50%", code=4001, status_code=400) from exc
        if percent <= 0 or percent >= 100:
            raise AppException(message="压缩百分比需要大于 0 且小于 100", code=4001, status_code=400)
        return max(1, int(current_bytes * percent / 100))

    multiplier = 1024
    number_text = raw
    if raw.endswith("mb"):
        multiplier = 1024 * 1024
        number_text = raw[:-2]
    elif raw.endswith("m"):
        multiplier = 1024 * 1024
        number_text = raw[:-1]
    elif raw.endswith("kb"):
        number_text = raw[:-2]
    elif raw.endswith("k"):
        number_text = raw[:-1]
    elif raw.endswith("bytes"):
        multiplier = 1
        number_text = raw[:-5]
    elif raw.endswith("byte"):
        multiplier = 1
        number_text = raw[:-4]
    elif raw.endswith("b"):
        multiplier = 1
        number_text = raw[:-1]

    try:
        target_bytes = int(float(number_text) * multiplier)
    except ValueError as exc:
        raise AppException(message="目标大小格式无效，请输入数字，例如 512", code=4001, status_code=400) from exc

    if target_bytes <= 0:
        raise AppException(message="目标大小必须大于 0", code=4001, status_code=400)

    max_bytes = get_settings().max_upload_size_mb * 1024 * 1024
    if target_bytes > max_bytes:
        raise AppException(
            message=f"目标大小不能超过 {get_settings().max_upload_size_mb}MB",
            code=4001,
            status_code=400,
        )
    return target_bytes


def _resolve_target_format(source_suffix: str, output_format: str = "original") -> tuple[str, str]:
    if output_format == "original":
        if source_suffix in IMAGE_FORMATS:
            return source_suffix, IMAGE_FORMATS[source_suffix]
        if source_suffix in HEIF_SUFFIXES:
            return source_suffix, "HEIF"
        return "png", "PNG"

    target_suffix = image_extension_from_format(output_format)
    return target_suffix, IMAGE_FORMATS.get(target_suffix, "PNG")


def _resolve_byte_size_format(image: Image.Image, source_suffix: str) -> tuple[str, str]:
    if source_suffix in {"jpg", "jpeg"}:
        return "jpg", "JPEG"
    if source_suffix == "webp":
        return "webp", "WEBP"
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        return "webp", "WEBP"
    return "jpg", "JPEG"


def _image_for_format(image: Image.Image, target_format: str) -> Image.Image:
    if target_format == "JPEG":
        return image.convert("RGB")
    if target_format == "WEBP":
        return image.convert("RGBA") if image.mode in {"RGBA", "LA"} else image.convert("RGB")
    return image


def _candidate_bytes(image: Image.Image, target_format: str, quality: int) -> bytes:
    stream = io.BytesIO()
    candidate = _image_for_format(image, target_format)
    save_kwargs: dict = {"format": target_format}
    if target_format in {"JPEG", "WEBP"}:
        save_kwargs["quality"] = max(1, min(int(quality), 95))
        save_kwargs["optimize"] = True
    elif target_format == "PNG":
        save_kwargs["optimize"] = True
        save_kwargs["compress_level"] = 9
    candidate.save(stream, **save_kwargs)
    return stream.getvalue()


def _resize_for_ratio(image: Image.Image, ratio: float) -> Image.Image:
    if ratio >= 0.999:
        return image.copy()
    width = max(1, int(image.width * ratio))
    height = max(1, int(image.height * ratio))
    return image.resize((width, height), resample=Image.Resampling.LANCZOS)


def _compress_file_size(input_path: str, output_dir: str, filename: str, target_kb: str | int | float) -> str:
    source_suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"
    if source_suffix in HEIF_SUFFIXES:
        _register_heif_support()

    current_bytes = Path(input_path).stat().st_size
    target_bytes = _parse_target_bytes(target_kb, current_bytes=current_bytes)
    if target_bytes >= current_bytes:
        current_kb = current_bytes / 1024
        raise AppException(
            message=f"目标大小必须小于当前文件大小，当前约 {current_kb:.1f}KB",
            code=4001,
            status_code=400,
        )

    image = load_image(input_path)
    target_suffix, target_format = _resolve_byte_size_format(image, source_suffix)
    target_path = Path(output_dir) / f"compressed.{target_suffix}"

    ratios = [1, 0.92, 0.84, 0.76, 0.68, 0.6, 0.52, 0.44, 0.36, 0.28, 0.2, 0.14, 0.1]
    qualities = [88, 80, 72, 64, 56, 48, 40, 32, 24, 16, 10]
    best: bytes | None = None
    for ratio in ratios:
        resized = _resize_for_ratio(image, ratio)
        for quality in qualities:
            data = _candidate_bytes(resized, target_format, quality)
            if len(data) <= target_bytes:
                target_path.write_bytes(data)
                return str(target_path)
            if best is None or len(data) < len(best):
                best = data

    if best is not None and len(best) <= target_bytes:
        target_path.write_bytes(best)
        return str(target_path)
    raise AppException(message="目标大小过小，当前图片无法压缩到该体积", code=4001, status_code=400)


def _shrink_dimensions(input_path: str, output_dir: str, filename: str, scale: int | str | float) -> str:
    try:
        scale_value = int(scale)
    except (TypeError, ValueError) as exc:
        raise AppException(message="宽高缩小倍数格式无效", code=4001, status_code=400) from exc

    if scale_value not in RESIZE_FACTORS:
        raise AppException(message="宽高缩小倍数只能是 2、3、4 或 10", code=4001, status_code=400)

    source_suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"
    if source_suffix in HEIF_SUFFIXES:
        _register_heif_support()

    image = load_image(input_path)
    resized = image.resize(
        (max(1, image.width // scale_value), max(1, image.height // scale_value)),
        resample=Image.Resampling.LANCZOS,
    )
    target_suffix, target_format = _resolve_target_format(source_suffix)
    if target_format == "HEIF":
        _register_heif_support()
    target_path = Path(output_dir) / f"compressed.{target_suffix}"
    return save_image(resized, target_path, target_format, quality=82)


def _legacy_compress(
    input_path: str,
    output_dir: str,
    filename: str,
    quality: int,
    output_format: str,
    max_width: int,
    max_height: int,
) -> str:
    source_suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"
    if source_suffix in HEIF_SUFFIXES:
        _register_heif_support()

    image = load_image(input_path)
    if max_width or max_height:
        limit = (
            max(1, int(max_width)) if int(max_width) > 0 else image.width,
            max(1, int(max_height)) if int(max_height) > 0 else image.height,
        )
        image.thumbnail(limit)

    target_suffix, target_format = _resolve_target_format(source_suffix, output_format)
    if target_format == "HEIF":
        _register_heif_support()
    target_path = Path(output_dir) / f"compressed.{target_suffix}"
    return save_image(image, target_path, target_format, quality=quality)


def run(
    input_path: str,
    output_dir: str,
    filename: str = "",
    mode: str = "byte_size",
    target_kb: str | int | float = "50%",
    scale: int | str | float = 2,
    quality: int = 75,
    output_format: str = "original",
    max_width: int = 0,
    max_height: int = 0,
    **_: dict,
) -> str:
    if (
        mode == "byte_size"
        and target_kb == "50%"
        and (quality != 75 or output_format != "original" or int(max_width) > 0 or int(max_height) > 0)
    ):
        return _legacy_compress(input_path, output_dir, filename, quality, output_format, max_width, max_height)
    if mode == "byte_size":
        return _compress_file_size(input_path, output_dir, filename, target_kb)
    if mode == "dimensions":
        return _shrink_dimensions(input_path, output_dir, filename, scale)
    if mode == "legacy":
        return _legacy_compress(input_path, output_dir, filename, quality, output_format, max_width, max_height)
    raise AppException(message="不支持的压缩方式", code=4001, status_code=400)
