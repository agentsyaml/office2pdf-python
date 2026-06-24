from __future__ import annotations

from collections.abc import Mapping
from importlib import import_module
from pathlib import Path
from typing import Protocol, runtime_checkable

from .exceptions import (
    Office2PdfError,
    Office2PdfIoError,
    Office2PdfParseError,
    Office2PdfRenderError,
    UnsupportedEncryptionError,
    UnsupportedFormatError,
    UnsupportedOptionError,
)
from ._results import _metrics_from_native, _result_from_native, _warning_from_native
from .models import ConversionResult, Format
from .options import ConvertOptions


@runtime_checkable
class _NativeModule(Protocol):
    def convert_bytes(
        self,
        data: bytes,
        format: str,
        options: dict[str, object] | None = None,
    ) -> Mapping[str, object]:
        ...

    def convert_path(
        self,
        path: str,
        options: dict[str, object] | None = None,
    ) -> Mapping[str, object]:
        ...


@runtime_checkable
class _NativeBytesModule(Protocol):
    def convert_bytes(
        self,
        data: bytes,
        format: str,
        options: dict[str, object] | None = None,
    ) -> Mapping[str, object]:
        ...


@runtime_checkable
class _NativePathModule(Protocol):
    def convert_path(
        self,
        path: str,
        options: dict[str, object] | None = None,
    ) -> Mapping[str, object]:
        ...


def _native_module() -> _NativeModule:
    module = import_module("office2pdf._native")
    if not isinstance(module, _NativeModule):
        raise TypeError("office2pdf._native does not provide the expected conversion functions")
    return module


def _native_error_types() -> tuple[type[BaseException], ...]:
    module = import_module("office2pdf._native")
    names = (
        "Office2PdfError",
        "UnsupportedFormatError",
        "Office2PdfIoError",
        "Office2PdfParseError",
        "Office2PdfRenderError",
        "UnsupportedEncryptionError",
        "UnsupportedOptionError",
    )
    errors: list[type[BaseException]] = []
    for name in names:
        candidate = getattr(module, name, None)
        if isinstance(candidate, type) and issubclass(candidate, BaseException):
            errors.append(candidate)
    return tuple(errors)


def _public_error_from_native(error: BaseException) -> Office2PdfError:
    message = str(error)
    match error.__class__.__name__:
        case "UnsupportedFormatError":
            return UnsupportedFormatError(message)
        case "Office2PdfIoError":
            return Office2PdfIoError(message)
        case "Office2PdfParseError":
            return Office2PdfParseError(message)
        case "Office2PdfRenderError":
            return Office2PdfRenderError(message)
        case "UnsupportedEncryptionError":
            return UnsupportedEncryptionError(message)
        case "UnsupportedOptionError":
            return UnsupportedOptionError(message)
        case _:
            return Office2PdfError(message)


def _native_bytes_module() -> _NativeBytesModule:
    module = import_module("office2pdf._native")
    if not isinstance(module, _NativeBytesModule):
        raise TypeError("office2pdf._native does not provide convert_bytes")
    return module


def _native_path_module() -> _NativePathModule:
    module = import_module("office2pdf._native")
    if not isinstance(module, _NativePathModule):
        raise TypeError("office2pdf._native does not provide convert_path")
    return module


def _native_options(options: ConvertOptions | None) -> dict[str, object]:
    return ConvertOptions().to_native() if options is None else options.to_native()


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
    native = _native_bytes_module()
    native_errors = _native_error_types()
    try:
        result = native.convert_bytes(payload, input_format.value, _native_options(options))
    except native_errors as error:
        raise _public_error_from_native(error) from error
    if not isinstance(result, Mapping):
        raise TypeError("native conversion result must be a mapping")
    return _result_from_native(result)


def convert_path(path: str | Path, options: ConvertOptions | None = None) -> ConversionResult:
    input_path = Path(path)
    infer_format(input_path)

    native = _native_path_module()
    native_errors = _native_error_types()
    try:
        result = native.convert_path(str(input_path), _native_options(options))
    except native_errors as error:
        raise _public_error_from_native(error) from error
    if not isinstance(result, Mapping):
        raise TypeError("native conversion result must be a mapping")
    return _result_from_native(result)


__all__ = [
    "convert_bytes",
    "convert_path",
    "infer_format",
    "_native_module",
    "_native_options",
    "_result_from_native",
    "_warning_from_native",
    "_metrics_from_native",
]
