"""文件说明：实现「GIF 图片制作」工具的后端逻辑。"""

from pathlib import Path

from app.core.exceptions import AppException
from app.utils.image_utils import extract_zip_to_dir, list_image_files, load_image, save_image


TOOL_META = {
    "slug": "gif-maker",
    "name": "GIF 图片制作",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, duration: int = 180, loop: int = 0, **_: dict) -> str:
    extracted = extract_zip_to_dir(input_path, Path(output_dir) / "gif-src")
    image_paths = list_image_files(extracted)
    if len(image_paths) < 2:
        raise AppException(message="请上传至少包含 2 张图片的 zip 压缩包", code=4002, status_code=400)

    frames = [load_image(path).convert("RGBA") for path in sorted(image_paths)]
    base_size = frames[0].size
    normalized_frames = [frame.resize(base_size) if frame.size != base_size else frame for frame in frames]
    target_path = Path(output_dir) / "generated.gif"
    return save_image(
        normalized_frames[0],
        target_path,
        "GIF",
        preserve_animation=True,
        frames=normalized_frames,
        durations=[max(20, int(duration))] * len(normalized_frames),
        loop=max(0, int(loop)),
    )
