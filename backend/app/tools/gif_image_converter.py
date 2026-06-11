from pathlib import Path

from PIL import ImageSequence

from app.core.exceptions import AppException
from app.utils.image_utils import ensure_rgb, load_image, save_image, zip_output_files


def convert_gif_image(input_path: str, output_dir: str, direction: str, pair: str) -> str:
    if pair not in {"png", "jpg"}:
        raise AppException(message="不支持的图片格式", code=4001, status_code=400)

    if direction == f"gif_to_{pair}":
        return _gif_to_images(input_path, output_dir, pair)
    if direction == f"{pair}_to_gif":
        return _image_to_gif(input_path, output_dir, pair)

    raise AppException(message="不支持的转换方向", code=4001, status_code=400)


def _gif_to_images(input_path: str, output_dir: str, output_suffix: str) -> str:
    source = Path(input_path)
    if source.suffix.lower() != ".gif":
        raise AppException(message="当前方向请上传 .gif 文件", code=4002, status_code=400)

    image = load_image(source)
    frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(image)]
    if not frames:
        raise AppException(message="GIF 中未找到可用帧", code=4002, status_code=400)

    output_format = "JPEG" if output_suffix == "jpg" else "PNG"
    if len(frames) == 1:
        target_path = Path(output_dir) / f"converted.{output_suffix}"
        frame = ensure_rgb(frames[0]) if output_suffix == "jpg" else frames[0]
        return save_image(frame, target_path, output_format, quality=92)

    frame_dir = Path(output_dir) / f"{output_suffix}-frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(frames, start=1):
        target_path = frame_dir / f"frame-{index:03d}.{output_suffix}"
        target_frame = ensure_rgb(frame) if output_suffix == "jpg" else frame
        save_image(target_frame, target_path, output_format, quality=92)

    return zip_output_files(frame_dir, Path(output_dir) / f"gif-{output_suffix}-frames.zip")


def _image_to_gif(input_path: str, output_dir: str, input_suffix: str) -> str:
    source = Path(input_path)
    allowed_suffixes = {"jpg", "jpeg"} if input_suffix == "jpg" else {input_suffix}
    if source.suffix.lower().lstrip(".") not in allowed_suffixes:
        suffix_label = ".jpg/.jpeg" if input_suffix == "jpg" else f".{input_suffix}"
        raise AppException(message=f"当前方向请上传 {suffix_label} 文件", code=4002, status_code=400)

    image = load_image(source).convert("RGBA")
    target_path = Path(output_dir) / "converted.gif"
    return save_image(image, target_path, "GIF")
