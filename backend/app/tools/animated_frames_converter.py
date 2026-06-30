"""文件说明：实现「GIF、WebP 等动图拆分合成」工具的后端逻辑。"""

import subprocess
import zipfile
from pathlib import Path

from PIL import Image

from app.core.exceptions import AppException
from app.tools.media_converter import _resolve_ffmpeg_path
from app.utils.image_utils import IMAGE_SUFFIXES, list_image_files, zip_output_files


TOOL_META = {
    "slug": "animated-frames-converter",
    "name": "GIF、WebP 等动图拆分合成",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


ANIMATION_FORMATS = {"gif", "apng", "webp", "avif"}
SPLIT_SUFFIXES = {
    "gif": {"gif"},
    "apng": {"png", "apng"},
    "webp": {"webp"},
    "avif": {"avif"},
}
PIL_FORMATS = {
    "gif": "GIF",
    "apng": "PNG",
    "webp": "WEBP",
    "avif": "AVIF",
}
OUTPUT_SUFFIXES = {
    "gif": "gif",
    "apng": "apng",
    "webp": "webp",
    "avif": "avif",
}
MAX_SPLIT_FRAMES = 300
MAX_COMPOSE_IMAGES = 240
MAX_ANIMATION_PIXELS = 2048 * 2048
MAX_ZIP_FILES = 260
MAX_ZIP_TOTAL_UNCOMPRESSED_BYTES = 120 * 1024 * 1024
MAX_ZIP_MEMBER_BYTES = 12 * 1024 * 1024


def run(
    input_path: str,
    output_dir: str,
    action: str = "split",
    input_format: str = "gif",
    output_format: str = "gif",
    fps: str | int = 12,
    **_: dict,
) -> str:
    if action == "split":
        return _split_animation(input_path, output_dir, input_format)
    if action == "compose":
        return _compose_animation(input_path, output_dir, output_format, fps)
    raise AppException(message="不支持的操作类型", code=4001, status_code=400)


def _normalize_format(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in ANIMATION_FORMATS:
        raise AppException(message="不支持的动图格式", code=4001, status_code=400)
    return normalized


def _resolve_ffmpeg_or_raise() -> str:
    ffmpeg_path = _resolve_ffmpeg_path()
    if not ffmpeg_path:
        raise AppException(message="未检测到 ffmpeg，请先安装后端依赖或在服务器安装 ffmpeg 后再使用该工具", code=5004, status_code=500)
    return ffmpeg_path


def _split_animation(input_path: str, output_dir: str, input_format: str) -> str:
    selected_format = _normalize_format(input_format)
    source_path = Path(input_path)
    suffix = source_path.suffix.lower().lstrip(".")
    if suffix not in SPLIT_SUFFIXES[selected_format]:
        raise AppException(message="上传文件格式与所选格式不一致，请重新选择。", code=4002, status_code=400)

    _ensure_selected_animation(source_path, selected_format)

    ffmpeg_path = _resolve_ffmpeg_or_raise()
    frame_dir = Path(output_dir) / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    frame_pattern = frame_dir / "frame-%04d.png"
    _run_ffmpeg(
        [ffmpeg_path, "-y", "-hide_banner", "-i", str(source_path), "-vsync", "0", str(frame_pattern)],
        avif_context=False,
    )

    if not any(frame_dir.glob("*.png")):
        raise AppException(message="未检测到多帧动画内容，无法拆分。", code=4002, status_code=400)

    return zip_output_files(frame_dir, Path(output_dir) / f"{selected_format}-frames.zip", "*.png")


def _ensure_selected_animation(source_path: Path, selected_format: str) -> None:
    try:
        with Image.open(source_path) as image:
            actual_format = (image.format or "").upper()
            if actual_format != PIL_FORMATS[selected_format]:
                raise AppException(message="上传文件格式与所选格式不一致，请重新选择。", code=4002, status_code=400)
            frame_count = getattr(image, "n_frames", 1)
            width, height = image.size
    except AppException:
        raise
    except Exception as exc:
        raise AppException(message="上传文件格式与所选格式不一致，请重新选择。", code=4002, status_code=400) from exc

    if frame_count <= 1:
        raise AppException(message="未检测到多帧动画内容，无法拆分。", code=4002, status_code=400)
    if frame_count > MAX_SPLIT_FRAMES:
        raise AppException(message=f"动图帧数过多，最多支持拆分 {MAX_SPLIT_FRAMES} 帧。", code=4002, status_code=400)
    if width * height > MAX_ANIMATION_PIXELS:
        raise AppException(message="动图尺寸过大，请压缩后再上传。", code=4002, status_code=400)


def _compose_animation(input_path: str, output_dir: str, output_format: str, fps: str | int) -> str:
    selected_format = _normalize_format(output_format)
    source_path = Path(input_path)
    if source_path.suffix.lower().lstrip(".") != "zip":
        raise AppException(message="合成动图请上传包含多张图片的 ZIP 压缩包。", code=4002, status_code=400)

    frame_rate = _normalize_fps(fps)
    extracted = _safe_extract_image_zip(source_path, Path(output_dir) / "compose-src")
    image_paths = sorted(list_image_files(extracted), key=lambda path: path.name.lower())
    if len(image_paths) < 2:
        raise AppException(message="请上传至少包含 2 张图片的 ZIP 压缩包。", code=4002, status_code=400)
    if len(image_paths) > MAX_COMPOSE_IMAGES:
        raise AppException(message=f"图片数量过多，最多支持 {MAX_COMPOSE_IMAGES} 张图片合成。", code=4002, status_code=400)

    sequence_dir = Path(output_dir) / "compose-frames"
    sequence_dir.mkdir(parents=True, exist_ok=True)
    _normalize_image_sequence(image_paths, sequence_dir)

    ffmpeg_path = _resolve_ffmpeg_or_raise()
    suffix = OUTPUT_SUFFIXES[selected_format]
    target_path = Path(output_dir) / f"generated.{suffix}"
    input_pattern = sequence_dir / "frame-%04d.png"
    command = _build_compose_command(ffmpeg_path, input_pattern, target_path, selected_format, frame_rate)
    _run_ffmpeg(command, avif_context=selected_format == "avif")

    if not target_path.exists() or target_path.stat().st_size == 0:
        raise AppException(message="动图合成失败，请确认上传图片可正常读取后重试。", code=5005, status_code=500)
    return str(target_path)


def _normalize_fps(value: str | int) -> int:
    try:
        fps = int(value)
    except (TypeError, ValueError) as exc:
        raise AppException(message="FPS 必须是有效整数。", code=4001, status_code=400) from exc
    if fps < 1 or fps > 60:
        raise AppException(message="FPS 建议设置在 1 到 60 之间。", code=4001, status_code=400)
    return fps


def _safe_extract_image_zip(input_path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    total_size = 0
    file_count = 0

    try:
        with zipfile.ZipFile(input_path) as archive:
            for member in archive.infolist():
                if member.is_dir() or member.filename.startswith("__MACOSX/"):
                    continue

                suffix = Path(member.filename).suffix.lower().lstrip(".")
                if suffix not in IMAGE_SUFFIXES:
                    continue

                file_count += 1
                if file_count > MAX_ZIP_FILES:
                    raise AppException(message=f"ZIP 内文件数量过多，最多支持 {MAX_ZIP_FILES} 个图片文件。", code=4002, status_code=400)
                if member.file_size > MAX_ZIP_MEMBER_BYTES:
                    raise AppException(message="ZIP 内单个图片文件过大，请压缩后再上传。", code=4002, status_code=400)

                total_size += member.file_size
                if total_size > MAX_ZIP_TOTAL_UNCOMPRESSED_BYTES:
                    raise AppException(message="ZIP 解压后体积过大，请减少图片数量或压缩后再上传。", code=4002, status_code=400)

                target = output_dir / f"{file_count:04d}-{Path(member.filename).name}"
                written = 0
                with archive.open(member) as src, target.open("wb") as dst:
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        written += len(chunk)
                        if written > MAX_ZIP_MEMBER_BYTES:
                            target.unlink(missing_ok=True)
                            raise AppException(message="ZIP 内单个图片文件过大，请压缩后再上传。", code=4002, status_code=400)
                        dst.write(chunk)
                extracted.append(target)
    except AppException:
        raise
    except zipfile.BadZipFile as exc:
        raise AppException(message="上传的 ZIP 压缩包无效。", code=4002, status_code=400) from exc

    return extracted


def _normalize_image_sequence(image_paths: list[Path], sequence_dir: Path) -> None:
    base_size: tuple[int, int] | None = None
    for index, image_path in enumerate(image_paths, start=1):
        try:
            with Image.open(image_path) as image:
                frame = image.convert("RGBA")
        except Exception as exc:
            raise AppException(message="图片读取失败，请确认 ZIP 中只包含可用图片。", code=4002, status_code=400) from exc

        if base_size is None:
            base_size = frame.size
            if base_size[0] * base_size[1] > MAX_ANIMATION_PIXELS:
                raise AppException(message="图片尺寸过大，请压缩后再上传。", code=4002, status_code=400)
        elif frame.size != base_size:
            frame = frame.resize(base_size)

        frame.save(sequence_dir / f"frame-{index:04d}.png", format="PNG")


def _build_compose_command(ffmpeg_path: str, input_pattern: Path, target_path: Path, output_format: str, fps: int) -> list[str]:
    common = [ffmpeg_path, "-y", "-hide_banner", "-framerate", str(fps), "-i", str(input_pattern)]
    if output_format == "gif":
        return [
            *common,
            "-filter_complex",
            "[0:v]split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=sierra2_4a",
            "-loop",
            "0",
            str(target_path),
        ]
    if output_format == "apng":
        return [*common, "-plays", "0", "-f", "apng", str(target_path)]
    if output_format == "webp":
        return [*common, "-c:v", "libwebp_anim", "-loop", "0", "-lossless", "0", "-q:v", "80", str(target_path)]
    if output_format == "avif":
        return [
            *common,
            "-c:v",
            "libaom-av1",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "30",
            "-b:v",
            "0",
            "-f",
            "avif",
            str(target_path),
        ]
    raise AppException(message="不支持的动图格式", code=4001, status_code=400)


def _run_ffmpeg(command: list[str], avif_context: bool) -> None:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=600, check=False)
    except subprocess.TimeoutExpired as exc:
        raise AppException(message="动图处理超时，请换用较小文件后重试。", code=5005, status_code=500) from exc
    except OSError as exc:
        raise AppException(message="ffmpeg 启动失败，请检查服务器运行环境。", code=5005, status_code=500) from exc

    if completed.returncode == 0:
        return

    error_text = (completed.stderr or completed.stdout or "").lower()
    if avif_context and ("unknown encoder" in error_text or "muxer" in error_text or "not suitable" in error_text):
        raise AppException(message="当前服务器暂不支持 AVIF 动图编码。", code=5005, status_code=500)
    raise AppException(message="动图处理失败，请确认文件格式正确后重试。", code=5005, status_code=500)
