"""文件说明：实现「PDF 转 Word」工具的后端逻辑。"""

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

    if not has_text:
        raise AppException(
            message="该 PDF 未检测到可编辑文本，可能是扫描件，暂不支持高保真转换",
            code=4002,
            status_code=400,
        )

    try:
        from pdf2docx import Converter
    except ImportError as exc:
        raise AppException(message="PDF 转 Word 组件未安装", code=5002, status_code=503) from exc

    target = Path(output_dir) / "pdf-to-word.docx"
    target.parent.mkdir(parents=True, exist_ok=True)
    converter = None
    try:
        converter = Converter(input_path)
        converter.convert(str(target), start=0, end=None)
    except Exception as exc:
        raise AppException(message=f"PDF 转 Word 失败：{exc}", code=4002, status_code=400) from exc
    finally:
        if converter is not None:
            converter.close()

    if not target.is_file() or target.stat().st_size == 0:
        raise AppException(message="PDF 转 Word 未生成有效文件", code=5002, status_code=500)
    return str(target)
