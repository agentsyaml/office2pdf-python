from __future__ import annotations

import sys
from typing import Any
from types import SimpleNamespace

import pytest

import office2pdf
from office2pdf import ConversionMetrics, FallbackUsedWarning, Format, ParseSkippedWarning
from office2pdf._native_bridge import _warning_from_native


def test_warning_from_native_dict() -> None:
    warning = _warning_from_native(
        {
            "kind": "FallbackUsed",
            "format": "PPTX",
            "from": "table",
            "to": "image",
            "message": "table rendered as image",
        }
    )

    assert isinstance(warning, FallbackUsedWarning)
    assert warning.format == "PPTX"
    assert warning.from_ == "table"
    assert warning.to == "image"
    assert warning.message == "table rendered as image"


def test_warning_from_native_partial_and_parse_skipped() -> None:
    partial = _warning_from_native(
        {
            "kind": "PartialElement",
            "format": "DOCX",
            "element": "image",
            "detail": "resolution lost",
        }
    )
    skipped = _warning_from_native(
        {
            "kind": "ParseSkipped",
            "format": "XLSX",
            "reason": "bad script",
        }
    )

    assert isinstance(partial, office2pdf.PartialElementWarning)
    assert partial.detail == "resolution lost"
    assert isinstance(skipped, ParseSkippedWarning)
    assert skipped.reason == "bad script"


def test_convert_result_from_native_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_convert_bytes(
        data: bytes,
        fmt: str,
        options: dict[str, object] | None,
    ) -> dict[str, Any]:
        captured.update(data=data, format=fmt, options=options)
        return {
            "pdf": b"%PDF-1.7",
            "warnings": [
                {"kind": "UnsupportedElement", "format": "DOCX", "element": "chart"},
                "legacy warning",
            ],
            "metrics": {
                "parse_duration": 0.1,
                "codegen_duration": 0.2,
                "compile_duration": 0.3,
                "total_duration": 0.6,
                "input_size_bytes": 2,
                "output_size_bytes": 3,
                "page_count": 4,
            },
        }

    monkeypatch.setitem(
        sys.modules,
        "office2pdf._native",
        SimpleNamespace(convert_bytes=fake_convert_bytes),
    )

    result = office2pdf.convert_bytes(bytearray(b"payload"), Format.XLSX)

    assert isinstance(result.pdf, bytes)
    assert result.metrics == ConversionMetrics(
        parse_duration=0.1,
        codegen_duration=0.2,
        compile_duration=0.3,
        total_duration=0.6,
        input_size_bytes=2,
        output_size_bytes=3,
        page_count=4,
    )
    assert len(result.warnings) == 2
    assert isinstance(result.warnings[0], office2pdf.UnsupportedElementWarning)
    assert isinstance(result.warnings[1], office2pdf.ConvertWarning)
    assert result.warning_messages == ("[DOCX] unsupported element: chart", "legacy warning")

    assert captured["format"] == "xlsx"


def test_convert_path_uses_extension_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_convert_path(path: str, _options: dict[str, object] | None) -> dict[str, Any]:
        calls.append(path)
        return {"pdf": b"%PDF-1.7", "warnings": (), "metrics": None}

    monkeypatch.setitem(
        sys.modules,
        "office2pdf._native",
        SimpleNamespace(convert_path=fake_convert_path),
    )

    assert office2pdf.convert_path("input.docx").pdf == b"%PDF-1.7"
    assert calls == ["input.docx"]

    with pytest.raises(ValueError, match="format must be one of"):
        office2pdf.convert_path("input.odt")


def test_native_error_classes_and_mapping() -> None:
    import office2pdf._native as native

    unsupported_format_error = getattr(native, "UnsupportedFormatError")
    io_error = getattr(native, "Office2PdfIoError")

    with pytest.raises(unsupported_format_error):
        native.convert_bytes(b"payload", "txt", None)

    with pytest.raises(io_error):
        native.convert_path("/tmp/office2pdf-missing-input.docx", None)


def test_public_api_translates_native_errors() -> None:
    with pytest.raises(office2pdf.Office2PdfIoError) as exc_info:
        office2pdf.convert_path("/tmp/office2pdf-missing-input.docx")

    assert isinstance(exc_info.value, OSError)
