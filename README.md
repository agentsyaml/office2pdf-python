# office2pdf-python

Python bindings for [`office2pdf`](https://github.com/developer0hye/office2pdf), a pure-Rust converter for DOCX, PPTX, and XLSX documents to PDF.

The package distribution is named `office2pdf-python`; the import package is `office2pdf`.

## Install

```bash
python -m pip install office2pdf-python
```

Supported Python versions are 3.10 through 3.14. Wheels use PyO3 `abi3-py310`, so one wheel can support all compatible CPython versions for the same platform. CI targets Linux, macOS, and Windows; release wheels cover Linux (x86_64 and aarch64, glibc and musl), macOS (Intel and Apple Silicon), and Windows (x86_64).

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

`Format` identifies the input Office format for byte-based conversion:

- `Format.DOCX` (`"docx"`)
- `Format.PPTX` (`"pptx"`)
- `Format.XLSX` (`"xlsx"`)

### `PdfStandard`

`PdfStandard` currently supports `pdf/a-2b`:

- canonical: `PdfStandard.PDF_A_2B`
- compatibility alias: `PdfStandard.PDF_A_2_B`

`PdfStandard.from_value()` accepts both forms and related normalizations (`"pdf/a-2b"`, `"pdfa2b"`).

### `XlsxUiScript`

`XlsxUiScript` selects which Excel user-interface language an XLSX conversion reproduces when resolving theme fonts (`<scheme val="minor"/>`):

- `XlsxUiScript.HANGUL` (`"hangul"`) — Korean UI Excel; upstream default.
- `XlsxUiScript.LATIN` (`"latin"`) — English, German, Danish, and other Latin-script Excel.

`XlsxUiScript.from_value()` accepts both names case-insensitively.

### `PaperSize`

- `PaperSize.A4`
- `PaperSize.LETTER`
- `PaperSize.LEGAL`

### `CustomPaperSize`

`CustomPaperSize(width: float, height: float)` stores explicit PDF point dimensions, matching upstream `PaperSize::Custom` (`1 point = 1/72 inch`).

### `ConvertOptions`

All options are stored in a Python dataclass and translated to native options via `to_native()`.

- `sheet_names: Sequence[str] | None`
- `sheet_filter: Sequence[str] | None`

  These are aliases for XLSX sheet selection. If both are provided, they must be equal.

- `xlsx_ui_script: XlsxUiScript | str | None`

  Picks the theme face an XLSX scheme font resolves to. `None` keeps the upstream default (`hangul`).

- `slide_range: SlideRange | str | None`

  `SlideRange` supports `"1-5"` parsing and also accepts explicit `SlideRange(1, 5)`. Values are normalized to `start-end` strings for native conversion.

- `include_hidden_slides: bool`

  Includes PPTX slides marked hidden. Defaults to `False`, matching PowerPoint PDF export. `slide_range` still counts source slide ordinals.

- `pdf_standard: PdfStandard | str | None`

  Only `pdf/a-2b` is supported at this version.

- `paper_size: PaperSize | CustomPaperSize | str | None`

  String values normalize to named page sizes.

- `font_paths: Sequence[str | pathlib.Path]`
- `last_resort_font_family: str | None`

  Family appended to every generated font chain, so a caller-provided face can cover glyphs the document's own fonts cannot. Must be non-empty. Load the face itself through `font_paths`.

- `landscape: bool | None`
- `tagged: bool | None`
- `pdf_ua: bool | None`
- `streaming: bool`
- `streaming_chunk_size: int | None`
- `include_warnings: bool`

Unsupported options are rejected to preserve API compatibility with upstream `office2pdf 0.9.1`:

- `page_range: str | None`
- `memory_limit_mb: int | None`

### `ConversionResult`

- `pdf: bytes`
- `warnings: tuple[ConvertWarning, ...]`
- `metrics: ConvertMetrics | None`
- `warning_messages: tuple[str, ...]` property collecting warning messages.

### Warning types

Warning payloads from the native layer are mapped to typed subclasses of `ConvertWarning`:

- `UnsupportedElementWarning(format, element)`
- `PartialElementWarning(format, element, detail)`
- `FallbackUsedWarning(format, from_, to)`
- `ParseSkippedWarning(format, reason)`
- and a base `ConvertWarning` for legacy/unknown forms.

### `ConvertMetrics`

- `parse_duration`
- `codegen_duration`
- `compile_duration`
- `total_duration`
- `input_size_bytes`
- `output_size_bytes`
- `page_count`

Duration fields are reported in seconds.

### Functions

```python
convert_bytes(data: bytes | bytearray | memoryview, format: Format | str, options: ConvertOptions | None = None) -> ConversionResult
convert_path(path: str | pathlib.Path, options: ConvertOptions | None = None) -> ConversionResult
infer_format(path: str | pathlib.Path) -> Format
```

- `infer_format()` reads the file suffix and accepts only `.docx`, `.pptx`, or `.xlsx`.
- `convert_path()` validates the file extension before conversion.
- `convert_bytes()` requires an explicit input `format`.

## Exceptions

Re-exported exception hierarchy:

- `Office2PdfError`
- `UnsupportedFormatError`
- `Office2PdfIoError`
- `Office2PdfParseError`
- `Office2PdfRenderError`
- `UnsupportedEncryptionError`
- `UnsupportedOptionError`

## API scope

Version `0.4.0` exposes the upstream `office2pdf 0.9.1` conversion API: file/bytes conversion, conversion options, structured warnings, metrics, and typed errors.

The upstream `pdf-ops` APIs (`page_count`, `merge`, `split`), internal IR/parser/render modules, TypeScript helpers, and WASM APIs are intentionally out of scope for this Python release.

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

The CI workflow runs tests on `ubuntu-latest`, `macos-latest`, and `windows-2022` for Python 3.10, 3.11, 3.12, 3.13, and 3.14. It builds and installs the extension as an editable package, runs pytest, and performs an import smoke test.

Release-style wheel building is checked once in a dedicated wheel smoke job. Full Linux, macOS, and Windows release wheels are built by the release workflow instead of every CI matrix job. Rust `fmt` and `clippy` run in a separate Ubuntu lint job.

## Release

The release workflow runs on `v*` tags or manual dispatch. It builds wheels for Linux (x86_64 and aarch64, manylinux_2_17 and musllinux_1_2), macOS (x86_64 and arm64), and Windows (x86_64) plus an sdist, then publishes with PyPI Trusted Publishing using GitHub OIDC (`id-token: write`). No PyPI API token is required. A manual dispatch builds and uploads the artifacts without publishing.

Before the first publish, configure PyPI with a pending trusted publisher:

- PyPI project name: `office2pdf-python`
- Owner: `agentsyaml`
- Repository: `office2pdf-python`
- Workflow: `release.yml`
- Environment: `pypi`

Create a matching GitHub environment named `pypi` and require manual approval for safer first releases. A pending trusted publisher can create the PyPI project on first use, but it does not reserve the project name before that first publish.

To publish a release automatically, update the version in `pyproject.toml` and `Cargo.toml`, commit the change, then push a matching tag:

```bash
git tag v0.4.0
git push origin v0.4.0
```

The tag push starts `.github/workflows/release.yml`, builds artifacts, publishes to PyPI after the `pypi` environment approval, and creates a GitHub Release for tag-triggered runs.

## Upstream dependency

This package wraps `office2pdf = "0.9.1"` from crates.io. The upstream project is Apache-2.0 licensed and hosted at <https://github.com/developer0hye/office2pdf>.
