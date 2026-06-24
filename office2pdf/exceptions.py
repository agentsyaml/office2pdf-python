from __future__ import annotations

class Office2PdfError(Exception):
    pass


class UnsupportedFormatError(Office2PdfError, ValueError):
    pass


class Office2PdfIoError(Office2PdfError, OSError):
    pass


class Office2PdfParseError(Office2PdfError, RuntimeError):
    pass


class Office2PdfRenderError(Office2PdfError, RuntimeError):
    pass


class UnsupportedEncryptionError(Office2PdfError, RuntimeError):
    pass


class UnsupportedOptionError(Office2PdfError, ValueError):
    pass


__all__ = [
    "Office2PdfError",
    "UnsupportedFormatError",
    "Office2PdfIoError",
    "Office2PdfParseError",
    "Office2PdfRenderError",
    "UnsupportedEncryptionError",
    "UnsupportedOptionError",
]
