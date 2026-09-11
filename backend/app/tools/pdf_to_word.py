"""文件说明：实现「PDF 转 Word」工具的后端逻辑。"""

import logging
import sys
import zipfile
from pathlib import Path

import pymupdf

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "pdf-to-word",
    "name": "PDF 转 Word",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}

LOGGER = logging.getLogger(__name__)


def _is_windows() -> bool:
    return sys.platform == "win32"


def _convert_with_word(input_path: str, target: Path) -> None:
    """在 Windows 桌面环境中使用 Microsoft Word 的 PDF 重排能力。"""
    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        raise RuntimeError("pywin32 未安装") from exc

    word = None
    document = None
    pythoncom.CoInitialize()
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        try:
            major_version = int(str(word.Version).split(".", 1)[0])
        except (TypeError, ValueError):
            major_version = 0
        if major_version < 15:
            raise RuntimeError("需要 Microsoft Word 2013 或更高版本")
        try:
            word.AutomationSecurity = 3
        except Exception:
            # 某些旧版 Word 不开放该属性，不影响 PDF 转换。
            pass

        document = word.Documents.Open(
            FileName=str(Path(input_path).resolve()),
            ConfirmConversions=False,
            ReadOnly=True,
            AddToRecentFiles=False,
            Visible=False,
            OpenAndRepair=True,
        )
        if document is None:
            raise RuntimeError("当前 Office 组件不支持通过 Word COM 打开 PDF")
        document.SaveAs2(
            FileName=str(target.resolve()),
            FileFormat=16,
            AddToRecentFiles=False,
        )
    finally:
        if document is not None:
            try:
                document.Close(SaveChanges=0)
            except Exception:
                LOGGER.warning("关闭 Word 文档失败", exc_info=True)
        if word is not None:
            try:
                word.Quit(SaveChanges=0)
            except Exception:
                LOGGER.warning("退出 Word 进程失败", exc_info=True)
        pythoncom.CoUninitialize()


def _convert_with_pdf2docx(input_path: str, target: Path) -> None:
    try:
        from pdf2docx import Converter
    except ImportError as exc:
        raise AppException(message="PDF 转 Word 组件未安装", code=5002, status_code=503) from exc

    converter = None
    try:
        converter = Converter(input_path)
        converter.convert(str(target), start=0, end=None)
    finally:
        if converter is not None:
            converter.close()


def _is_valid_docx(target: Path) -> bool:
    if not target.is_file() or target.stat().st_size == 0 or not zipfile.is_zipfile(target):
        return False
    try:
        with zipfile.ZipFile(target) as archive:
            return "word/document.xml" in archive.namelist()
    except (OSError, zipfile.BadZipFile):
        return False


def run(input_path: str, output_dir: str, **_: dict) -> str:
    try:
        with pymupdf.open(input_path) as pdf:
            if pdf.needs_pass:
                raise AppException(message="PDF 已加密，请先解除密码保护", code=4002, status_code=400)
            has_text = any(page.get_text("text").strip() for page in pdf)
    except AppException:
        raise
    except Exception as exc:
        raise AppException(message=f"无法读取 PDF 文件：{exc}", code=4002, status_code=400) from exc

    target = Path(output_dir) / "pdf-to-word.docx"
    target.parent.mkdir(parents=True, exist_ok=True)

    if _is_windows():
        try:
            target.unlink(missing_ok=True)
            _convert_with_word(input_path, target)
            if _is_valid_docx(target):
                return str(target)
            raise RuntimeError("Word 未生成有效的 DOCX 文件")
        except Exception as exc:
            LOGGER.warning("Microsoft Word 转换失败，将回退到 pdf2docx：%s", exc)
            target.unlink(missing_ok=True)

    if not has_text:
        raise AppException(
            message="该 PDF 未检测到可编辑文本，可能是扫描件，暂不支持高保真转换",
            code=4002,
            status_code=400,
        )

    try:
        _convert_with_pdf2docx(input_path, target)
    except AppException:
        raise
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise AppException(message=f"PDF 转 Word 失败：{exc}", code=4002, status_code=400) from exc

    if not _is_valid_docx(target):
        target.unlink(missing_ok=True)
        raise AppException(message="PDF 转 Word 未生成有效文件", code=5002, status_code=500)
    return str(target)
