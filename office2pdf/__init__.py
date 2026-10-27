from __future__ import annotations

from importlib import metadata

from ._native_bridge import (
    _metrics_from_native,
    _native_module,
    _native_options,
    _result_from_native,
    _warning_from_native,
    convert_bytes,
    convert_path,
    infer_format,
)
from .exceptions import (
    Office2PdfError,
    Office2PdfIoError,
    Office2PdfParseError,
    Office2PdfRenderError,
    UnsupportedEncryptionError,
    UnsupportedFormatError,
    UnsupportedOptionError,
)
from .models import (
    ConversionMetrics,
    ConversionResult,
    ConvertMetrics,
    ConvertWarning,
    CustomPaperSize,
    FallbackUsedWarning,
    Format,
    ParseSkippedWarning,
    PaperSize,
    PartialElementWarning,
    PdfStandard,
    SlideRange,
    UnsupportedElementWarning,
    XlsxUiScript,
)
from .options import ConvertOptions


try:
    __version__ = metadata.version("office2pdf-python")
except metadata.PackageNotFoundError:
    __version__ = "0.4.1"


__all__ = [
    "ConversionResult",
    "ConversionMetrics",
    "ConvertMetrics",
    "ConvertOptions",
    "Format",
    "PaperSize",
    "CustomPaperSize",
    "PdfStandard",
    "XlsxUiScript",
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
