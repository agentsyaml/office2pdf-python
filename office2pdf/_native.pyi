from __future__ import annotations

from typing import Mapping, Sequence, TypedDict

class Office2PdfError(Exception): ...


class UnsupportedFormatError(Office2PdfError): ...


class Office2PdfIoError(Office2PdfError): ...


class Office2PdfParseError(Office2PdfError): ...


class Office2PdfRenderError(Office2PdfError): ...


class UnsupportedEncryptionError(Office2PdfError): ...


class UnsupportedOptionError(Office2PdfError): ...

__version__: str

ConvertWarningData = TypedDict(
    "ConvertWarningData",
    {
        "kind": str,
        "format": str,
        "element": str,
        "detail": str,
        "from": str,
        "to": str,
        "reason": str,
        "message": str,
    },
    total=False,
)


class ConvertMetricsData(TypedDict):
    parse_duration: float
    codegen_duration: float
    compile_duration: float
    total_duration: float
    input_size_bytes: int
    output_size_bytes: int
    page_count: int


class ConvertResultData(TypedDict, total=False):
    pdf: bytes
    warnings: Sequence[str | ConvertWarningData]
    metrics: ConvertMetricsData | None

def convert_bytes(
    data: bytes,
    format: str,
    options: Mapping[str, object] | None = None,
) -> ConvertResultData: ...

def convert_path(
    path: str,
    options: Mapping[str, object] | None = None,
) -> ConvertResultData: ...
