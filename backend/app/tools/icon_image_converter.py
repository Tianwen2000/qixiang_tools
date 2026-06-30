"""文件说明：实现 icon image converter 工具的后端逻辑。"""

from pathlib import Path

from PIL import Image, ImageFilter

from app.core.exceptions import AppException
from app.utils.image_utils import ensure_rgb, load_image, save_image


ICON_SUFFIXES = {"ico", "icns"}
ICON_FORMATS = {"ico": "ICO", "icns": "ICNS"}
ICON_SAVE_SIZES = {
    "ico": [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    "icns": [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)],
}


def convert_icon_image(input_path: str, output_dir: str, direction: str, icon_suffix: str) -> str:
    if icon_suffix not in ICON_SUFFIXES:
        raise AppException(message="不支持的图标格式", code=4001, status_code=400)

    if direction in {f"png_to_{icon_suffix}", f"jpg_to_{icon_suffix}"}:
        source_suffix = direction.split("_to_")[0]
        return _image_to_icon(input_path, output_dir, source_suffix, icon_suffix)

    if direction in {f"{icon_suffix}_to_png", f"{icon_suffix}_to_jpg"}:
        target_suffix = direction.split("_to_")[1]
        return _icon_to_image(input_path, output_dir, icon_suffix, target_suffix)

    raise AppException(message="不支持的转换方向", code=4001, status_code=400)


def _validate_suffix(path: Path, allowed: set[str], label: str) -> None:
    suffix = path.suffix.lower().lstrip(".")
    if suffix not in allowed:
        raise AppException(message=f"当前方向请上传 {label} 文件", code=4002, status_code=400)


def _validate_actual_format(image: Image.Image, allowed_formats: set[str], label: str) -> None:
    actual = (image.format or "").upper()
    if actual and actual not in allowed_formats:
        raise AppException(message=f"上传文件格式与所选方向不一致，请上传 {label} 文件", code=4002, status_code=400)


def _sharpen_icon_frame(frame: Image.Image, side: int) -> Image.Image:
    if side <= 64:
        return frame.filter(ImageFilter.UnsharpMask(radius=0.45, percent=140, threshold=3))
    if side <= 128:
        return frame.filter(ImageFilter.UnsharpMask(radius=0.6, percent=115, threshold=4))
    return frame


def _icon_frame_for_size(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    side = min(size)
    ratio = min(side / rgba.width, side / rgba.height)
    resized_size = (
        max(1, round(rgba.width * ratio)),
        max(1, round(rgba.height * ratio)),
    )
    resized = rgba.resize(resized_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((side - resized.width) // 2, (side - resized.height) // 2))
    return _sharpen_icon_frame(canvas, side)


def _build_icon_frames(image: Image.Image, icon_suffix: str) -> list[Image.Image]:
    sizes = ICON_SAVE_SIZES[icon_suffix]
    return [_icon_frame_for_size(image, size) for size in sorted(sizes, reverse=True)]


def _image_to_icon(input_path: str, output_dir: str, source_suffix: str, icon_suffix: str) -> str:
    source = Path(input_path)
    allowed_suffixes = {"jpg", "jpeg"} if source_suffix == "jpg" else {source_suffix}
    suffix_label = ".jpg/.jpeg" if source_suffix == "jpg" else f".{source_suffix}"
    _validate_suffix(source, allowed_suffixes, suffix_label)

    image = load_image(source)
    allowed_formats = {"JPEG"} if source_suffix == "jpg" else {"PNG"}
    _validate_actual_format(image, allowed_formats, suffix_label)

    frames = _build_icon_frames(image, icon_suffix)
    target_path = Path(output_dir) / f"converted.{icon_suffix}"
    frames[0].save(
        target_path,
        format=ICON_FORMATS[icon_suffix],
        append_images=frames[1:] if icon_suffix == "ico" else frames,
        sizes=ICON_SAVE_SIZES[icon_suffix],
    )
    return str(target_path)


def _icon_to_image(input_path: str, output_dir: str, icon_suffix: str, target_suffix: str) -> str:
    source = Path(input_path)
    _validate_suffix(source, {icon_suffix}, f".{icon_suffix}")

    image = load_image(source)
    _validate_actual_format(image, {ICON_FORMATS[icon_suffix]}, f".{icon_suffix}")

    target_format = "JPEG" if target_suffix == "jpg" else "PNG"
    target_path = Path(output_dir) / f"converted.{target_suffix}"
    frame = ensure_rgb(image) if target_format == "JPEG" else image.convert("RGBA")
    return save_image(frame, target_path, target_format, quality=92)
