from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .exceptions import UnsupportedOptionError
from .models import CustomPaperSize, PaperSize, PdfStandard, SlideRange, XlsxUiScript


@dataclass(frozen=True, slots=True)
class ConvertOptions:
    sheet_names: Sequence[str] | None = None
    slide_range: SlideRange | str | None = None
    pdf_standard: PdfStandard | str | None = None
    paper_size: PaperSize | CustomPaperSize | str | None = None
    font_paths: Sequence[str | Path] = ()
    landscape: bool | None = None
    tagged: bool | None = None
    pdf_ua: bool | None = None
    streaming: bool = False
    streaming_chunk_size: int | None = None
    include_warnings: bool = True
    sheet_filter: Sequence[str] | None = None
    page_range: str | None = None
    memory_limit_mb: int | None = None
    # Appended so positional callers of the previous release keep their meaning.
    xlsx_ui_script: XlsxUiScript | str | None = None
    include_hidden_slides: bool = False
    last_resort_font_family: str | None = None

    @staticmethod
    def _ensure_strings(values: Sequence[str] | None, field_name: str) -> tuple[str, ...] | None:
        if values is None:
            return None
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
            raise TypeError(f"{field_name} must be a sequence of strings")
        for value in values:
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a sequence of strings")
        return tuple(values)

    @staticmethod
    def _ensure_paths(values: Sequence[str | Path]) -> tuple[str, ...]:
        if values is None:
            return ()
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
            raise TypeError("font_paths must be a sequence of strings or pathlib.Path values")
        return tuple(str(path) for path in values)

    def to_native(self) -> dict[str, object]:
        if self.page_range is not None:
            raise UnsupportedOptionError("page_range is not supported by upstream office2pdf 0.9")
        if self.memory_limit_mb is not None:
            raise UnsupportedOptionError("memory_limit_mb is not supported by upstream office2pdf 0.9")

        sheet_names = self._ensure_strings(self.sheet_names, "sheet_names")
        sheet_filter = self._ensure_strings(self.sheet_filter, "sheet_filter")

        if sheet_names is not None and sheet_filter is not None and tuple(sheet_names) != tuple(sheet_filter):
            raise UnsupportedOptionError("sheet_names and sheet_filter are aliases and must match")
        if sheet_names is None:
            sheet_names = sheet_filter

        if isinstance(self.slide_range, str):
            slide_range = str(SlideRange.parse(self.slide_range))
        elif isinstance(self.slide_range, SlideRange):
            slide_range = str(self.slide_range)
        elif self.slide_range is None:
            slide_range = None
        else:
            raise TypeError("slide_range must be a SlideRange or string")

        if isinstance(self.xlsx_ui_script, str):
            xlsx_ui_script = XlsxUiScript.from_value(self.xlsx_ui_script).value
        elif isinstance(self.xlsx_ui_script, XlsxUiScript):
            xlsx_ui_script = self.xlsx_ui_script.value
        elif self.xlsx_ui_script is None:
            xlsx_ui_script = None
        else:
            raise TypeError("xlsx_ui_script must be an XlsxUiScript or string")

        if isinstance(self.pdf_standard, str):
            pdf_standard = PdfStandard.from_value(self.pdf_standard).value
        elif self.pdf_standard is None:
            pdf_standard = None
        else:
            pdf_standard = self.pdf_standard.value

        if isinstance(self.paper_size, str):
            paper_size = ("Named", PaperSize.from_value(self.paper_size).value)
        elif isinstance(self.paper_size, PaperSize):
            paper_size = ("Named", self.paper_size.value)
        elif isinstance(self.paper_size, CustomPaperSize):
            paper_size = ("Custom", self.paper_size.width, self.paper_size.height)
        elif self.paper_size is None:
            paper_size = None
        else:
            raise TypeError("paper_size must be PaperSize, CustomPaperSize, or string")

        if self.tagged is not None and not isinstance(self.tagged, bool):
            raise TypeError("tagged must be bool")
        if self.pdf_ua is not None and not isinstance(self.pdf_ua, bool):
            raise TypeError("pdf_ua must be bool")
        if self.landscape is not None and not isinstance(self.landscape, bool):
            raise TypeError("landscape must be bool")
        if not isinstance(self.include_hidden_slides, bool):
            raise TypeError("include_hidden_slides must be bool")
        if self.last_resort_font_family is not None:
            if not isinstance(self.last_resort_font_family, str):
                raise TypeError("last_resort_font_family must be a string")
            if not self.last_resort_font_family.strip():
                raise ValueError("last_resort_font_family must not be empty")
        if not isinstance(self.streaming, bool):
            raise TypeError("streaming must be bool")
        if not isinstance(self.include_warnings, bool):
            raise TypeError("include_warnings must be bool")
        if self.streaming_chunk_size is not None and (
            not isinstance(self.streaming_chunk_size, int) or self.streaming_chunk_size < 1
        ):
            raise ValueError("streaming_chunk_size must be a positive integer")

        return {
            "sheet_names": sheet_names,
            "sheet_filter": sheet_filter,
            "xlsx_ui_script": xlsx_ui_script,
            "slide_range": slide_range,
            "include_hidden_slides": self.include_hidden_slides,
            "pdf_standard": pdf_standard,
            "paper_size": paper_size,
            "font_paths": self._ensure_paths(self.font_paths),
            "last_resort_font_family": self.last_resort_font_family,
            "landscape": self.landscape,
            "tagged": self.tagged,
            "pdf_ua": self.pdf_ua,
            "streaming": self.streaming,
            "streaming_chunk_size": self.streaming_chunk_size,
            "include_warnings": self.include_warnings,
            "page_range": None,
            "memory_limit_mb": None,
        }


__all__ = ["ConvertOptions"]
