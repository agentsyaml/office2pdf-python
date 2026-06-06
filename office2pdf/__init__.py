from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from importlib import import_module, metadata
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    __version__ = metadata.version("office2pdf-python")
except metadata.PackageNotFoundError:
    __version__ = "0.1.0"


class Format(Enum):
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"

    @classmethod
    def from_value(cls, value: Format | str) -> Format:
        if isinstance(value, cls):
            return value
        normalized = str(value).lower().lstrip(".")
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError("format must be one of: docx, pptx, xlsx")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConvertOptions:
    page_range: str | None = None
    sheet_filter: Sequence[str] | None = None
    slide_range: str | None = None
    paper_size: str | None = None
    landscape: bool | None = None
    font_paths: Sequence[str | Path] = field(default_factory=tuple)
    pdf_standard: str | None = None
    include_warnings: bool = True
    memory_limit_mb: int | None = None
    streaming: bool = False

    def to_native(self) -> dict[str, Any]:
        if self.page_range is not None:
            raise ValueError("page_range is not supported by upstream office2pdf 0.6")
        if self.memory_limit_mb is not None:
            raise ValueError("memory_limit_mb is not supported by upstream office2pdf 0.6")
        if self.sheet_filter is not None and not all(isinstance(item, str) for item in self.sheet_filter):
            raise TypeError("sheet_filter must contain only strings")
        if self.font_paths is not None and not all(isinstance(item, (str, Path)) for item in self.font_paths):
            raise TypeError("font_paths must contain only str or pathlib.Path values")

        return {
            "page_range": None,
            "sheet_filter": list(self.sheet_filter) if self.sheet_filter is not None else None,
            "slide_range": self.slide_range,
            "paper_size": self.paper_size,
            "landscape": self.landscape,
            "font_paths": [str(path) for path in self.font_paths],
            "pdf_standard": self.pdf_standard,
            "include_warnings": self.include_warnings,
            "memory_limit_mb": None,
            "streaming": self.streaming,
        }


@dataclass(frozen=True)
class ConversionResult:
    pdf: bytes
    warnings: tuple[str, ...] = ()
    metrics: Mapping[str, Any] | None = None


def infer_format(path: str | Path) -> Format:
    suffix = Path(path).suffix.lower().lstrip(".")
    if not suffix:
        raise ValueError("path has no extension; expected .docx, .pptx, or .xlsx")
    return Format.from_value(suffix)


def convert_bytes(
    data: bytes | bytearray | memoryview,
    format: Format | str,
    options: ConvertOptions | None = None,
) -> ConversionResult:
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes-like")
    payload = bytes(data)
    if not payload:
        raise ValueError("data must not be empty")

    input_format = Format.from_value(format)
    native = _native_module()
    raw = native.convert_bytes(payload, input_format.value, _native_options(options))
    return _result_from_native(raw)


def convert_path(path: str | Path, options: ConvertOptions | None = None) -> ConversionResult:
    input_path = Path(path)
    infer_format(input_path)

    native = _native_module()
    raw = native.convert_path(str(input_path), _native_options(options))
    return _result_from_native(raw)


def _native_options(options: ConvertOptions | None) -> dict[str, Any]:
    return ConvertOptions().to_native() if options is None else options.to_native()


def _native_module() -> Any:
    return import_module("office2pdf._native")


def _result_from_native(raw: Mapping[str, Any]) -> ConversionResult:
    pdf = raw.get("pdf")
    if not isinstance(pdf, bytes):
        raise TypeError("native conversion result did not contain PDF bytes")

    warnings = raw.get("warnings", ())
    if not isinstance(warnings, Sequence) or isinstance(warnings, (str, bytes, bytearray)):
        raise TypeError("native conversion result warnings must be a sequence of strings")

    return ConversionResult(
        pdf=pdf,
        warnings=tuple(str(warning) for warning in warnings),
        metrics=raw.get("metrics"),
    )


__all__ = [
    "ConversionResult",
    "ConvertOptions",
    "Format",
    "__version__",
    "convert_bytes",
    "convert_path",
    "infer_format",
]
