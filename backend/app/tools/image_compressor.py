from pathlib import Path

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


def _register_heif_support() -> None:
    try:
        from pillow_heif import register_heif_opener
    except Exception as exc:  # pragma: no cover - dependency safety net
        raise AppException(message=f"当前环境暂不支持 HEIC/HEIF 压缩：{exc}", code=5002, status_code=500) from exc
    register_heif_opener()


def _resolve_target_format(source_suffix: str, output_format: str) -> tuple[str, str]:
    if output_format == "original":
        if source_suffix in IMAGE_FORMATS:
            return source_suffix, IMAGE_FORMATS[source_suffix]
        if source_suffix in HEIF_SUFFIXES:
            return source_suffix, "HEIF"
        return "png", "PNG"

    target_suffix = image_extension_from_format(output_format)
    return target_suffix, IMAGE_FORMATS.get(target_suffix, "PNG")


def run(
    input_path: str,
    output_dir: str,
    filename: str = "",
    quality: int = 75,
    output_format: str = "original",
    max_width: int = 0,
    max_height: int = 0,
    **_: dict,
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
