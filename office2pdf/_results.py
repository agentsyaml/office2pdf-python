from __future__ import annotations

from collections.abc import Mapping, Sequence

from .models import (
    ConversionResult,
    ConvertMetrics,
    ConvertWarning,
    FallbackUsedWarning,
    ParseSkippedWarning,
    PartialElementWarning,
    UnsupportedElementWarning,
)


def _as_string(raw: dict[str, object], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise TypeError(f"native {key} must be a string")
    return value


def _as_int(raw: dict[str, object], key: str) -> int:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"native {key} must be numeric")
    return int(value)


def _as_float(raw: dict[str, object], key: str) -> float:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"native {key} must be numeric")
    return float(value)


def _warning_message(raw: dict[str, object], message_key: str, fallback: str) -> str:
    value = raw.get(message_key)
    return value if isinstance(value, str) else fallback


def _warning_from_native(raw: object) -> ConvertWarning:
    if isinstance(raw, str):
        return ConvertWarning(raw)
    if not isinstance(raw, Mapping):
        raise TypeError("native warning must be a string or mapping")

    data = dict(raw)
    format_name = str(data.get("format", ""))
    kind = data.get("kind")

    if kind == "UnsupportedElement":
        return UnsupportedElementWarning(
            format=format_name,
            element=_as_string(data, "element"),
            message=_warning_message(
                data,
                "message",
                f"[{format_name}] unsupported element: {_as_string(data, 'element')}",
            ),
        )
    if kind == "PartialElement":
        element = _as_string(data, "element")
        return PartialElementWarning(
            format=format_name,
            element=element,
            detail=_as_string(data, "detail"),
            message=_warning_message(
                data,
                "message",
                f"[{format_name}] partial rendering of {element}: {_as_string(data, 'detail')}",
            ),
        )
    if kind == "FallbackUsed":
        from_value = _as_string(data, "from")
        to_value = _as_string(data, "to")
        return FallbackUsedWarning(
            format=format_name,
            from_=from_value,
            to=to_value,
            message=_warning_message(
                data,
                "message",
                f"[{format_name}] fallback: {from_value} rendered as {to_value}",
            ),
        )
    if kind == "ParseSkipped":
        return ParseSkippedWarning(
            format=format_name,
            reason=_as_string(data, "reason"),
            message=_warning_message(
                data,
                "message",
                f"[{format_name}] skipped: {_as_string(data, 'reason')}",
            ),
        )

    return ConvertWarning(message=_warning_message(data, "message", ""), kind=str(kind))


def _metrics_from_native(raw: object) -> ConvertMetrics | None:
    if raw is None:
        return None
    if not isinstance(raw, Mapping):
        raise TypeError("native metrics must be a mapping")

    data = dict(raw)
    return ConvertMetrics(
        parse_duration=_as_float(data, "parse_duration"),
        codegen_duration=_as_float(data, "codegen_duration"),
        compile_duration=_as_float(data, "compile_duration"),
        total_duration=_as_float(data, "total_duration"),
        input_size_bytes=_as_int(data, "input_size_bytes"),
        output_size_bytes=_as_int(data, "output_size_bytes"),
        page_count=_as_int(data, "page_count"),
    )


def _result_from_native(raw: Mapping[str, object]) -> ConversionResult:
    data = dict(raw)
    pdf = data.get("pdf")
    if not isinstance(pdf, (bytes, bytearray)):
        raise TypeError("native conversion result did not contain PDF bytes")

    raw_warnings = data.get("warnings", ())
    if isinstance(raw_warnings, (str, bytes, bytearray)):
        raise TypeError("native conversion result warnings must be a sequence of values")
    if not isinstance(raw_warnings, Sequence):
        raise TypeError("native conversion result warnings must be a sequence of values")

    warnings = tuple(_warning_from_native(warning) for warning in raw_warnings)

    return ConversionResult(
        pdf=bytes(pdf),
        warnings=warnings,
        metrics=_metrics_from_native(data.get("metrics")),
    )


__all__ = ["_metrics_from_native", "_result_from_native", "_warning_from_native"]
