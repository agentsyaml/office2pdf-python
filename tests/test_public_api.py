from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

import office2pdf
from office2pdf import ConversionResult, ConvertOptions, Format


def test_import_and_public_api() -> None:
    assert office2pdf.__version__
    assert Format.DOCX.value == "docx"
    assert str(Format.PPTX) == "pptx"
    assert office2pdf.__all__ == [
        "ConversionResult",
        "ConvertOptions",
        "Format",
        "__version__",
        "convert_bytes",
        "convert_path",
        "infer_format",
    ]


def test_options_to_native_mapping() -> None:
    options = ConvertOptions(
        sheet_filter=("Sheet1", "Summary"),
        slide_range="1-3",
        paper_size="a4",
        landscape=True,
        font_paths=("/tmp/fonts",),
        pdf_standard="pdf/a-2b",
        include_warnings=False,
        streaming=True,
    )

    assert options.to_native() == {
        "page_range": None,
        "sheet_filter": ["Sheet1", "Summary"],
        "slide_range": "1-3",
        "paper_size": "a4",
        "landscape": True,
        "font_paths": ["/tmp/fonts"],
        "pdf_standard": "pdf/a-2b",
        "include_warnings": False,
        "memory_limit_mb": None,
        "streaming": True,
    }


@pytest.mark.parametrize(
    "options, message",
    [
        (ConvertOptions(page_range="1-2"), "page_range is not supported"),
        (ConvertOptions(memory_limit_mb=128), "memory_limit_mb is not supported"),
    ],
)
def test_unsupported_upstream_options_raise(options: ConvertOptions, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        options.to_native()


@pytest.mark.parametrize(
    "path, expected",
    [
        ("report.docx", Format.DOCX),
        ("slides.PPTX", Format.PPTX),
        ("book.xlsx", Format.XLSX),
    ],
)
def test_infer_format(path: str, expected: Format) -> None:
    assert office2pdf.infer_format(path) is expected


def test_infer_format_rejects_unknown_extension() -> None:
    with pytest.raises(ValueError, match="format must be one of"):
        office2pdf.infer_format("notes.txt")


def test_convert_bytes_rejects_empty_input_without_native_import() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        office2pdf.convert_bytes(b"", Format.DOCX)


def test_convert_bytes_rejects_invalid_format_without_native_import() -> None:
    with pytest.raises(ValueError, match="format must be one of"):
        office2pdf.convert_bytes(b"not-office", "txt")


def test_convert_bytes_uses_native_module(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_convert_bytes(data: bytes, format: str, options: dict[str, object]) -> dict[str, object]:
        captured.update(data=data, format=format, options=options)
        return {"pdf": b"%PDF-1.7", "warnings": ["warning"], "metrics": {"page_count": 1}}

    monkeypatch.setitem(
        sys.modules,
        "office2pdf._native",
        SimpleNamespace(convert_bytes=fake_convert_bytes),
    )

    result = office2pdf.convert_bytes(bytearray(b"payload"), Format.XLSX)

    assert result == ConversionResult(
        pdf=b"%PDF-1.7",
        warnings=("warning",),
        metrics={"page_count": 1},
    )
    assert captured["data"] == b"payload"
    assert captured["format"] == "xlsx"


def test_convert_path_validates_extension_before_native(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_convert_path(path: str, _options: dict[str, object]) -> dict[str, object]:
        calls.append(path)
        return {"pdf": b"%PDF-1.7", "warnings": [], "metrics": None}

    monkeypatch.setitem(
        sys.modules,
        "office2pdf._native",
        SimpleNamespace(convert_path=fake_convert_path),
    )

    assert office2pdf.convert_path("input.docx").pdf == b"%PDF-1.7"
    assert calls == ["input.docx"]

    with pytest.raises(ValueError, match="format must be one of"):
        office2pdf.convert_path("input.odt")
