from pathlib import Path

from PIL import ImageSequence

from app.core.exceptions import AppException
from app.utils.image_utils import load_image, save_image


TOOL_META = {
    "slug": "gif-scaler",
    "name": "GIF 图片缩放",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, scale_percent: int = 50, **_: dict) -> str:
    scale_percent = int(scale_percent)
    if scale_percent <= 0:
        raise AppException(message="缩放比例必须大于 0", code=4001, status_code=400)

    image = load_image(input_path)
    if not getattr(image, "is_animated", False):
        raise AppException(message="上传的文件不是 GIF 动图", code=4002, status_code=400)

    frames = []
    durations = []
    for frame in ImageSequence.Iterator(image):
        width = max(1, frame.width * scale_percent // 100)
        height = max(1, frame.height * scale_percent // 100)
        frames.append(frame.convert("RGBA").resize((width, height)))
        durations.append(frame.info.get("duration", image.info.get("duration", 120)))

    target_path = Path(output_dir) / "scaled.gif"
    return save_image(
        frames[0],
        target_path,
        "GIF",
        preserve_animation=True,
        frames=frames,
        durations=durations,
        loop=image.info.get("loop", 0),
    )
