"""文件说明：实现「Word 转 PDF」工具的后端逻辑。"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "docx-to-pdf",
    "name": "Word 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def find_libreoffice_executable() -> str | None:
    configured = os.getenv("LIBREOFFICE_PATH", "").strip()
    candidates = [
        configured,
        shutil.which("soffice") or "",
        shutil.which("libreoffice") or "",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for variable in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
        if base_path := os.getenv(variable, "").strip():
            candidates.append(str(Path(base_path) / "LibreOffice" / "program" / "soffice.exe"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    return None


def _convert_with_libreoffice(input_path: str, target: Path) -> None:
    executable = find_libreoffice_executable()
    if not executable:
        raise AppException(
            message="未安装 LibreOffice，无法进行高保真 Word 转 PDF",
            code=5002,
            status_code=503,
        )

    source = Path(input_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="qixiang-libreoffice-") as profile_dir:
        command = [
            executable,
            "--headless",
            "--nologo",
            "--nodefault",
            "--nofirststartwizard",
            "--nolockcheck",
            f"-env:UserInstallation={Path(profile_dir).resolve().as_uri()}",
            "--convert-to",
            "pdf:writer_pdf_Export",
            "--outdir",
            str(target.parent.resolve()),
            str(source),
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=120,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except subprocess.TimeoutExpired as exc:
            raise AppException(message="Word 转 PDF 超时", code=5002, status_code=504) from exc
        except OSError as exc:
            raise AppException(message=f"无法启动 LibreOffice：{exc}", code=5002, status_code=503) from exc

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "未知错误").strip()[:300]
        raise AppException(message=f"LibreOffice 转换失败：{detail}", code=4002, status_code=400)

    converted = target.parent / f"{source.stem}.pdf"
    if not converted.is_file() or converted.stat().st_size == 0:
        raise AppException(message="LibreOffice 未生成有效 PDF 文件", code=5002, status_code=500)
    if converted != target:
        converted.replace(target)


def run(input_path: str, output_dir: str, **_: dict) -> str:
    target = Path(output_dir) / "word-to-pdf.pdf"
    _convert_with_libreoffice(input_path, target)
    return str(target)
