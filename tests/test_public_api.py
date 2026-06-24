from __future__ import annotations

import pytest

import office2pdf
from office2pdf import (
    ConversionMetrics,
    ConversionResult,
    ConvertMetrics,
    ConvertOptions,
    ConvertWarning,
    FallbackUsedWarning,
    Format,
    PdfStandard,
    PaperSize,
    ParseSkippedWarning,
    SlideRange,
    UnsupportedElementWarning,
    PartialElementWarning,
    CustomPaperSize,
)


def test_import_and_public_api() -> None:
    assert office2pdf.__version__
    assert Format.DOCX.value == "docx"
    assert str(Format.PPTX) == "pptx"
    assert office2pdf.__all__ == [
        "ConversionResult",
        "ConversionMetrics",
        "ConvertMetrics",
        "ConvertOptions",
        "Format",
        "PaperSize",
        "CustomPaperSize",
        "PdfStandard",
        "SlideRange",
        "ConvertWarning",
        "UnsupportedElementWarning",
        "PartialElementWarning",
        "FallbackUsedWarning",
        "ParseSkippedWarning",
        "Office2PdfError",
        "UnsupportedFormatError",
        "Office2PdfIoError",
        "Office2PdfParseError",
        "Office2PdfRenderError",
        "UnsupportedEncryptionError",
        "UnsupportedOptionError",
        "__version__",
        "convert_bytes",
        "convert_path",
        "infer_format",
    ]


def test_import_exception_reexports() -> None:
    from office2pdf import exceptions as exp

    assert exp.Office2PdfError is office2pdf.Office2PdfError
    assert exp.UnsupportedFormatError is office2pdf.UnsupportedFormatError
    assert issubclass(office2pdf.UnsupportedFormatError, ValueError)
    assert issubclass(office2pdf.Office2PdfIoError, OSError)
    assert issubclass(office2pdf.Office2PdfParseError, RuntimeError)
    assert issubclass(office2pdf.Office2PdfRenderError, RuntimeError)
    assert issubclass(office2pdf.UnsupportedEncryptionError, RuntimeError)
    assert issubclass(office2pdf.UnsupportedOptionError, ValueError)


def test_slide_range_parse_and_repr() -> None:
    slide_range = SlideRange.parse("2-4")
    assert slide_range.start == 2
    assert slide_range.end == 4
    assert str(slide_range) == "2-4"

    assert SlideRange.parse("5") == SlideRange(5, 5)


def test_parse_options_with_alias_and_conflict() -> None:
    options = ConvertOptions(
        sheet_filter=("Sheet1", "Summary"),
        slide_range=SlideRange(1, 3),
        paper_size=PaperSize.A4,
        landscape=True,
        font_paths=("/tmp/fonts",),
        pdf_standard=PdfStandard.PDF_A_2_B,
        tagged=True,
        pdf_ua=False,
        include_warnings=False,
        streaming=True,
        streaming_chunk_size=1024,
    )

    assert options.to_native() == {
        "sheet_names": ("Sheet1", "Summary"),
        "sheet_filter": ("Sheet1", "Summary"),
        "slide_range": "1-3",
        "paper_size": ("Named", "a4"),
        "landscape": True,
        "tagged": True,
        "pdf_ua": False,
        "font_paths": ("/tmp/fonts",),
        "pdf_standard": "pdf/a-2b",
        "include_warnings": False,
        "page_range": None,
        "memory_limit_mb": None,
        "streaming": True,
        "streaming_chunk_size": 1024,
    }


@pytest.mark.parametrize(
    "options, message",
    [
        (
            ConvertOptions(sheet_names=("A",), sheet_filter=("B",)),
            "sheet_names and sheet_filter",
        ),
        (ConvertOptions(page_range="1-2"), "page_range"),
        (ConvertOptions(memory_limit_mb=128), "memory_limit_mb"),
    ],
)
def test_unsupported_compatibility_options_raise(options: ConvertOptions, message: str) -> None:
    from office2pdf import UnsupportedOptionError

    with pytest.raises(UnsupportedOptionError, match=message):
        options.to_native()


def test_options_custom_paper_size_to_native() -> None:
    options = ConvertOptions(paper_size=CustomPaperSize(width=100.5, height=200.0))

    assert options.to_native()["paper_size"] == ("Custom", 100.5, 200.0)


def test_options_slide_range_parse_from_string() -> None:
    options = ConvertOptions(slide_range="2-7")
    assert options.to_native()["slide_range"] == "2-7"


def test_warning_compatibility_property() -> None:
    result = ConversionResult(
        pdf=b"%PDF-1.7",
        warnings=(
            UnsupportedElementWarning(format="DOCX", element="chart"),
            ConvertWarning("legacy", kind="Legacy"),
        ),
        metrics=None,
    )

    assert result.warning_messages == ("[DOCX] unsupported element: chart", "legacy")


def test_convert_bytes_rejects_empty_input_without_native_import() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        office2pdf.convert_bytes(b"", Format.DOCX)
