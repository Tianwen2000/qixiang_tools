import shutil
from pathlib import Path

from PIL import Image, ImageFilter

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.utils.image_utils import IMAGE_FORMATS, load_image, save_image


TOOL_META = {
    "slug": "image-upscaler",
    "name": "图片增大",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def _parse_target_bytes(value: str | int | float) -> int:
    raw = str(value).strip().lower().replace(" ", "")
    if not raw:
        raise AppException(message="请输入目标大小", code=4001, status_code=400)

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
        raise AppException(message="目标大小格式无效，请输入数字，例如 1024", code=4001, status_code=400) from exc

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


def _padding_bytes(length: int) -> bytes:
    marker = b"\nQIXIANG_IMAGE_BYTE_PADDING\n"
    if length <= len(marker):
        return marker[:length]
    return marker + (b"\0" * (length - len(marker)))


def _resolve_suffix(filename: str, input_path: str) -> str:
    suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"
    if suffix not in IMAGE_FORMATS:
        return "png"
    return suffix


def _expand_file_size(input_path: str, output_dir: str, filename: str, target_kb: str | int | float) -> str:
    load_image(input_path)
    suffix = _resolve_suffix(filename, input_path)
    target_bytes = _parse_target_bytes(target_kb)
    target_path = Path(output_dir) / f"expanded.{suffix}"
    shutil.copyfile(input_path, target_path)

    current_bytes = target_path.stat().st_size
    if target_bytes <= current_bytes:
        current_kb = current_bytes / 1024
        raise AppException(
            message=f"目标大小必须大于当前文件大小，当前约 {current_kb:.1f}KB",
            code=4001,
            status_code=400,
        )

    with target_path.open("ab") as file:
        file.write(_padding_bytes(target_bytes - current_bytes))

    load_image(target_path)
    return str(target_path)


def _expand_dimensions(input_path: str, output_dir: str, filename: str, scale: int | str | float) -> str:
    try:
        scale_value = int(scale)
    except (TypeError, ValueError) as exc:
        raise AppException(message="宽高倍数格式无效", code=4001, status_code=400) from exc

    if scale_value not in {2, 3, 4, 10}:
        raise AppException(message="宽高倍数只能是 2、3、4 或 10", code=4001, status_code=400)

    image = load_image(input_path)
    enlarged = image.resize(
        (image.width * scale_value, image.height * scale_value),
        resample=Image.Resampling.LANCZOS,
    )
    enhanced = enlarged.filter(ImageFilter.UnsharpMask(radius=1.8, percent=110, threshold=3))

    suffix = _resolve_suffix(filename, input_path)
    target_format = IMAGE_FORMATS.get(suffix, "PNG")
    target_path = Path(output_dir) / f"resized.{suffix}"
    return save_image(enhanced, target_path, target_format, quality=92)


def run(
    input_path: str,
    output_dir: str,
    filename: str = "",
    mode: str = "byte_size",
    target_kb: str | int | float = 1024,
    scale: int | str | float = 2,
    **_: dict,
) -> str:
    if mode == "byte_size":
        return _expand_file_size(input_path, output_dir, filename, target_kb)
    if mode == "dimensions":
        return _expand_dimensions(input_path, output_dir, filename, scale)
    raise AppException(message="不支持的增大方式", code=4001, status_code=400)
