import shutil
import subprocess
from pathlib import Path

from app.core.exceptions import AppException


CONVERSION_SPECS = {
    "mp3-flac-converter": {
        "mp3_to_flac": {
            "input_suffix": "mp3",
            "output_suffix": "flac",
            "args": ["-i", "{input}", "-vn", "-c:a", "flac", "{output}"],
        },
        "flac_to_mp3": {
            "input_suffix": "flac",
            "output_suffix": "mp3",
            "args": ["-i", "{input}", "-vn", "-c:a", "libmp3lame", "-q:a", "2", "{output}"],
        },
    },
    "wav-mp3-converter": {
        "wav_to_mp3": {
            "input_suffix": "wav",
            "output_suffix": "mp3",
            "args": ["-i", "{input}", "-vn", "-c:a", "libmp3lame", "-q:a", "2", "{output}"],
        },
        "mp3_to_wav": {
            "input_suffix": "mp3",
            "output_suffix": "wav",
            "args": ["-i", "{input}", "-vn", "-c:a", "pcm_s16le", "{output}"],
        },
    },
    "mov-mp4-converter": {
        "mov_to_mp4": {
            "input_suffix": "mov",
            "output_suffix": "mp4",
            "args": ["-i", "{input}", "-map", "0", "-c", "copy", "-movflags", "+faststart", "{output}"],
            "fallback_args": [
                "-i",
                "{input}",
                "-map",
                "0",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                "{output}",
            ],
        },
        "mp4_to_mov": {
            "input_suffix": "mp4",
            "output_suffix": "mov",
            "args": ["-i", "{input}", "-map", "0", "-c", "copy", "{output}"],
            "fallback_args": [
                "-i",
                "{input}",
                "-map",
                "0",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "{output}",
            ],
        },
    },
    "mp3-mp4-converter": {
        "mp3_to_mp4": {
            "input_suffix": "mp3",
            "output_suffix": "mp4",
            "args": ["-i", "{input}", "-vn", "-c:a", "aac", "-b:a", "192k", "{output}"],
        },
        "mp4_to_mp3": {
            "input_suffix": "mp4",
            "output_suffix": "mp3",
            "args": ["-i", "{input}", "-vn", "-c:a", "libmp3lame", "-q:a", "2", "{output}"],
        },
    },
    "gif-mp4-converter": {
        "gif_to_mp4": {
            "input_suffix": "gif",
            "output_suffix": "mp4",
            "args": [
                "-i",
                "{input}",
                "-movflags",
                "+faststart",
                "-pix_fmt",
                "yuv420p",
                "-vf",
                "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                "-c:v",
                "libx264",
                "-an",
                "{output}",
            ],
        },
        "mp4_to_gif": {
            "input_suffix": "mp4",
            "output_suffix": "gif",
            "args": ["-i", "{input}", "-vf", "fps=15,scale=640:-1:flags=lanczos", "{output}"],
        },
    },
}


def convert_media(input_path: str, output_dir: str, tool_slug: str, direction: str) -> str:
    tool_specs = CONVERSION_SPECS.get(tool_slug)
    if not tool_specs or direction not in tool_specs:
        raise AppException(message="不支持的转换方向", code=4001, status_code=400)

    source_path = Path(input_path)
    source_suffix = source_path.suffix.lower().lstrip(".")
    spec = tool_specs[direction]
    expected_suffix = spec["input_suffix"]
    if source_suffix != expected_suffix:
        raise AppException(message=f"当前方向请上传 .{expected_suffix} 文件", code=4002, status_code=400)

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise AppException(message="未检测到 ffmpeg，请先在服务器安装 ffmpeg 后再使用音视频转换工具", code=5004, status_code=500)

    output_suffix = spec["output_suffix"]
    target_path = Path(output_dir) / f"converted.{output_suffix}"
    commands = [spec["args"]]
    if spec.get("fallback_args"):
        commands.append(spec["fallback_args"])

    last_error = ""
    for args in commands:
        rendered_args = [item.format(input=str(source_path), output=str(target_path)) for item in args]
        completed = subprocess.run(
            [ffmpeg_path, "-y", "-hide_banner", *rendered_args],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        if completed.returncode == 0 and target_path.exists():
            return str(target_path)
        last_error = (completed.stderr or completed.stdout or "").strip()
        target_path.unlink(missing_ok=True)

    detail = f"：{last_error[-300:]}" if last_error else ""
    raise AppException(message=f"音视频转换失败{detail}", code=5005, status_code=500)
