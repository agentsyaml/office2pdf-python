from __future__ import annotations

from typing import Any, Mapping

__version__: str

def convert_bytes(data: bytes, format: str, options: Mapping[str, Any] | None = None) -> dict[str, Any]: ...

def convert_path(path: str, options: Mapping[str, Any] | None = None) -> dict[str, Any]: ...
