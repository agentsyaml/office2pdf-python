from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from office2pdf import convert_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="office2pdf",
        description="Convert DOCX, PPTX, or XLSX files to PDF.",
    )
    parser.add_argument("input", type=Path, help="Input Office file (.docx, .pptx, or .xlsx)")
    parser.add_argument("output", type=Path, help="Output PDF file")
    args = parser.parse_args(argv)

    try:
        result = convert_path(args.input)
        args.output.write_bytes(result.pdf)
    except Exception as exc:
        print(f"office2pdf: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
