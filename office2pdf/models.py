from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Format(Enum):
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"

    @classmethod
    def from_value(cls, value: Format | str) -> "Format":
        if isinstance(value, cls):
            return value
        normalized = str(value).lower().lstrip(".")
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError("format must be one of: docx, pptx, xlsx")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SlideRange:
    start: int
    end: int

    def __post_init__(self) -> None:
        if not isinstance(self.start, int) or not isinstance(self.end, int):
            raise TypeError("slide range must contain integers")
        if self.start < 1 or self.end < 1:
            raise ValueError("slide numbers must be >= 1")
        if self.start > self.end:
            raise ValueError("start slide must be <= end slide")

    @classmethod
    def parse(cls, value: str) -> "SlideRange":
        start_text, sep, end_text = str(value).strip().partition("-")
        if sep:
            return cls(int(start_text), int(end_text))
        number = int(start_text)
        return cls(number, number)

    def __str__(self) -> str:
        return f"{self.start}-{self.end}"


class PaperSize(Enum):
    A4 = "a4"
    LETTER = "letter"
    LEGAL = "legal"

    @classmethod
    def from_value(cls, value: str) -> "PaperSize":
        normalized = str(value).lower().strip()
        for item in cls:
            if item.value == normalized:
                return item
        raise ValueError("paper size must be one of: a4, letter, legal")


@dataclass(frozen=True, slots=True)
class CustomPaperSize:
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("custom paper size dimensions must be positive")


class PdfStandard(Enum):
    PDF_A_2B = "pdf/a-2b"
    PDF_A_2_B = "pdf/a-2b"

    @classmethod
    def from_value(cls, value: PdfStandard | str) -> "PdfStandard":
        if isinstance(value, cls):
            return value
        normalized = str(value).lower().replace("_", "-").replace(" ", "")
        if normalized in {"pdf/a-2b", "pdfa2b", "pdf_a_2b"}:
            return cls.PDF_A_2B
        raise ValueError("unsupported pdf_standard; expected 'pdf/a-2b'")


class XlsxUiScript(Enum):
    HANGUL = "hangul"
    LATIN = "latin"

    @classmethod
    def from_value(cls, value: XlsxUiScript | str) -> "XlsxUiScript":
        if isinstance(value, cls):
            return value
        normalized = str(value).lower().strip()
        for item in cls:
            if item.value == normalized:
                return item
        raise ValueError("xlsx_ui_script must be one of: hangul, latin")


@dataclass(frozen=True, slots=True)
class ConvertWarning:
    message: str = ""
    kind: str = "Legacy"

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class UnsupportedElementWarning(ConvertWarning):
    format: str = ""
    element: str = ""

    def __post_init__(self) -> None:
        if not self.format:
            raise ValueError("format is required")
        if not self.element:
            raise ValueError("element is required")
        object.__setattr__(self, "kind", "UnsupportedElement")
        if not self.message:
            object.__setattr__(self, "message", f"[{self.format}] unsupported element: {self.element}")


@dataclass(frozen=True, slots=True)
class PartialElementWarning(ConvertWarning):
    format: str = ""
    element: str = ""
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.format:
            raise ValueError("format is required")
        if not self.element:
            raise ValueError("element is required")
        if not self.detail:
            raise ValueError("detail is required")
        object.__setattr__(self, "kind", "PartialElement")
        if not self.message:
            object.__setattr__(
                self,
                "message",
                f"[{self.format}] partial rendering of {self.element}: {self.detail}",
            )


@dataclass(frozen=True, slots=True)
class FallbackUsedWarning(ConvertWarning):
    format: str = ""
    from_: str = ""
    to: str = ""

    def __post_init__(self) -> None:
        if not self.format:
            raise ValueError("format is required")
        if not self.from_:
            raise ValueError("from is required")
        if not self.to:
            raise ValueError("to is required")
        object.__setattr__(self, "kind", "FallbackUsed")
        if not self.message:
            object.__setattr__(self, "message", f"[{self.format}] fallback: {self.from_} rendered as {self.to}")


@dataclass(frozen=True, slots=True)
class ParseSkippedWarning(ConvertWarning):
    format: str = ""
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.format:
            raise ValueError("format is required")
        if not self.reason:
            raise ValueError("reason is required")
        object.__setattr__(self, "kind", "ParseSkipped")
        if not self.message:
            object.__setattr__(self, "message", f"[{self.format}] skipped: {self.reason}")


@dataclass(frozen=True, slots=True)
class ConvertMetrics:
    parse_duration: float
    codegen_duration: float
    compile_duration: float
    total_duration: float
    input_size_bytes: int
    output_size_bytes: int
    page_count: int


ConversionMetrics = ConvertMetrics


@dataclass(frozen=True, slots=True)
class ConversionResult:
    pdf: bytes
    warnings: tuple[ConvertWarning, ...] = ()
    metrics: ConvertMetrics | None = None

    @property
    def warning_messages(self) -> tuple[str, ...]:
        return tuple(warning.message for warning in self.warnings)


__all__ = [
    "Format",
    "SlideRange",
    "PaperSize",
    "CustomPaperSize",
    "PdfStandard",
    "XlsxUiScript",
    "ConvertWarning",
    "UnsupportedElementWarning",
    "PartialElementWarning",
    "FallbackUsedWarning",
    "ParseSkippedWarning",
    "ConvertMetrics",
    "ConversionMetrics",
    "ConversionResult",
]
