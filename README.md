# office2pdf-python

Python bindings for [`office2pdf`](https://github.com/developer0hye/office2pdf), a pure-Rust converter for DOCX, PPTX, and XLSX documents to PDF.

The package distribution is named `office2pdf-python`; the import package is `office2pdf`.

## Install

```bash
python -m pip install office2pdf-python
```

Supported Python versions are 3.10 through 3.14. Wheels use PyO3 `abi3-py310`, so one wheel can support all compatible CPython versions for the same platform. CI targets Linux, macOS, and Windows.

## Usage

```python
from pathlib import Path

from office2pdf import ConvertOptions, Format, convert_bytes, convert_path

result = convert_path("report.docx")
Path("report.pdf").write_bytes(result.pdf)

options = ConvertOptions(paper_size="a4", landscape=False, include_warnings=True)
data = Path("slides.pptx").read_bytes()
result = convert_bytes(data, Format.PPTX, options)
Path("slides.pdf").write_bytes(result.pdf)
```

## CLI

The package also installs an `office2pdf` command:

```bash
office2pdf input.docx output.pdf
```

The CLI accepts DOCX, PPTX, and XLSX input paths and writes the converted PDF bytes to the output path.

## API

### `Format`

Enum values: `Format.DOCX`, `Format.PPTX`, and `Format.XLSX`.

### `ConvertOptions`

Dataclass fields:

- `page_range: str | None` — rejected when set because `office2pdf 0.6.0` does not expose a native field for it.
- `sheet_filter: Sequence[str] | None` — maps to upstream `sheet_names` for XLSX conversion.
- `slide_range: str | None` — accepts upstream strings like `"1-5"` or `"3"`.
- `paper_size: str | None` — accepts upstream `"a4"`, `"letter"`, or `"legal"`.
- `landscape: bool | None` — maps to upstream orientation control.
- `font_paths: Sequence[str | pathlib.Path]` — additional font directories.
- `pdf_standard: str | None` — currently supports `"pdf/a-2b"`.
- `include_warnings: bool` — controls whether returned warnings are included in `ConversionResult`.
- `memory_limit_mb: int | None` — rejected when set because `office2pdf 0.6.0` does not expose a native field for it.
- `streaming: bool` — enables upstream streaming mode for supported formats.

### `ConversionResult`

Dataclass fields:

- `pdf: bytes`
- `warnings: tuple[str, ...]`
- `metrics: Mapping[str, Any] | None`

### Functions

```python
convert_bytes(data: bytes | bytearray | memoryview, format: Format | str, options: ConvertOptions | None = None) -> ConversionResult
convert_path(path: str | pathlib.Path, options: ConvertOptions | None = None) -> ConversionResult
infer_format(path: str | pathlib.Path) -> Format
```

`convert_path()` validates the file extension before calling the native extension. `convert_bytes()` requires an explicit format.

## Local development

Install Rust and Python 3.10 or newer. For local development, create and activate a virtual environment before running `maturin develop`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip maturin pytest
maturin develop --locked
python -m pytest
cargo fmt --check
cargo clippy --all-targets -- -D warnings
```

Build artifacts:

```bash
maturin build --locked --release --compatibility pypi
maturin sdist
```

No LibreOffice, Docker, Chromium, or external system service is required by this binding. Conversion behavior comes from the upstream pure-Rust crate.

## CI

The CI workflow runs on `ubuntu-latest`, `macos-latest`, and `windows-latest` for Python 3.10, 3.11, 3.12, 3.13, and 3.14. It builds and installs the extension as an editable package, runs pytest, performs an import smoke test, and builds a wheel. Rust `fmt` and `clippy` run once on Ubuntu with Python 3.12.

## Release

The release workflow runs on `v*` tags or manual dispatch. It builds Linux, macOS, and Windows wheels plus an sdist, then publishes with PyPI Trusted Publishing using GitHub OIDC (`id-token: write`).

Before publishing, configure the PyPI project `office2pdf-python` with a trusted publisher for this repository, workflow file `.github/workflows/release.yml`, and environment `pypi`.

## Upstream dependency

This package wraps `office2pdf = "0.6"` from crates.io. The upstream project is Apache-2.0 licensed and hosted at <https://github.com/developer0hye/office2pdf>.
