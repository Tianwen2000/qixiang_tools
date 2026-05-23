from pathlib import Path

from PIL import Image
from PIL import ImageSequence

from app.core.exceptions import AppException
from app.utils.image_utils import extract_zip_to_dir, save_image


TOOL_META = {
    "slug": "gif-merger",
    "name": "GIF 图片合并",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    extracted = extract_zip_to_dir(input_path, Path(output_dir) / "gif-merge-src")
    gif_paths = sorted(path for path in extracted if path.suffix.lower() == ".gif")
    if len(gif_paths) < 2:
        raise AppException(message="请上传至少包含 2 个 GIF 的 zip 压缩包", code=4002, status_code=400)

    frames = []
    durations = []
    for gif_path in gif_paths:
        image = Image.open(gif_path)
        for frame in ImageSequence.Iterator(image):
            frames.append(frame.convert("RGBA"))
            durations.append(frame.info.get("duration", 120))

    if not frames:
        raise AppException(message="GIF 中未找到可用帧", code=4002, status_code=400)

    base_size = frames[0].size
    normalized = [frame.resize(base_size) if frame.size != base_size else frame for frame in frames]
    target_path = Path(output_dir) / "merged.gif"
    return save_image(
        normalized[0],
        target_path,
        "GIF",
        preserve_animation=True,
        frames=normalized,
        durations=durations,
        loop=0,
    )
