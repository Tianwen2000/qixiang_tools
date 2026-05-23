from pathlib import Path

from PIL import ImageSequence

from app.core.exceptions import AppException
from app.utils.image_utils import load_image, save_image, zip_output_files


TOOL_META = {
    "slug": "gif-splitter",
    "name": "GIF 图片分解",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    image = load_image(input_path)
    if not getattr(image, "is_animated", False):
        raise AppException(message="上传的文件不是 GIF 动图", code=4002, status_code=400)

    frame_dir = Path(output_dir) / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(ImageSequence.Iterator(image), start=1):
        save_image(frame.convert("RGBA"), frame_dir / f"frame-{index:03d}.png", "PNG")

    return zip_output_files(frame_dir, Path(output_dir) / "gif-frames.zip")
