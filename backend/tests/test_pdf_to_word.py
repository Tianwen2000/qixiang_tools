from pathlib import Path

import pymupdf
import pytest
from docx import Document

from app.core.exceptions import AppException
from app.tools import pdf_to_word


def _make_pdf(path: Path, text: str = "") -> None:
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        if text:
            page.insert_text((72, 72), text)
        pdf.save(path)


def _write_docx(target: Path) -> None:
    document = Document()
    document.add_paragraph("converted")
    document.save(target)


def test_windows_prefers_word_conversion(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    output_dir = tmp_path / "output"
    _make_pdf(source, "PDF text")

    monkeypatch.setattr(pdf_to_word, "_is_windows", lambda: True)
    monkeypatch.setattr(pdf_to_word, "_convert_with_word", lambda _source, target: _write_docx(target))
    monkeypatch.setattr(
        pdf_to_word,
        "_convert_with_pdf2docx",
        lambda *_args: pytest.fail("Word 成功时不应调用 pdf2docx"),
    )

    result = Path(pdf_to_word.run(str(source), str(output_dir)))

    assert pdf_to_word._is_valid_docx(result)


def test_windows_falls_back_when_word_fails(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    output_dir = tmp_path / "output"
    _make_pdf(source, "PDF text")

    monkeypatch.setattr(pdf_to_word, "_is_windows", lambda: True)
    monkeypatch.setattr(
        pdf_to_word,
        "_convert_with_word",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("Word unavailable")),
    )
    monkeypatch.setattr(pdf_to_word, "_convert_with_pdf2docx", lambda _source, target: _write_docx(target))

    result = Path(pdf_to_word.run(str(source), str(output_dir)))

    assert pdf_to_word._is_valid_docx(result)


def test_windows_word_can_handle_pdf_without_editable_text(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "scan.pdf"
    output_dir = tmp_path / "output"
    _make_pdf(source)

    monkeypatch.setattr(pdf_to_word, "_is_windows", lambda: True)
    monkeypatch.setattr(pdf_to_word, "_convert_with_word", lambda _source, target: _write_docx(target))

    result = Path(pdf_to_word.run(str(source), str(output_dir)))

    assert pdf_to_word._is_valid_docx(result)


def test_non_windows_still_rejects_pdf_without_editable_text(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "scan.pdf"
    _make_pdf(source)
    monkeypatch.setattr(pdf_to_word, "_is_windows", lambda: False)

    with pytest.raises(AppException) as exc_info:
        pdf_to_word.run(str(source), str(tmp_path / "output"))

    assert "未检测到可编辑文本" in exc_info.value.message
