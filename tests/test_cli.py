from __future__ import annotations

from pathlib import Path

import pytest

from office2pdf import ConversionResult
from office2pdf import cli


def test_cli_writes_pdf(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, Path] = {}

    def fake_convert_path(path: Path) -> ConversionResult:
        captured["path"] = path
        return ConversionResult(pdf=b"%PDF-1.7", warnings=(), metrics=None)

    monkeypatch.setattr(cli, "convert_path", fake_convert_path)
    output = tmp_path / "report.pdf"

    assert cli.main(["report.docx", str(output)]) == 0
    assert captured["path"] == Path("report.docx")
    assert output.read_bytes() == b"%PDF-1.7"


def test_cli_reports_conversion_errors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def fake_convert_path(_path: Path) -> ConversionResult:
        raise RuntimeError("conversion failed")

    monkeypatch.setattr(cli, "convert_path", fake_convert_path)

    assert cli.main(["report.docx", str(tmp_path / "report.pdf")]) == 1
    assert "conversion failed" in capsys.readouterr().err


def test_cli_requires_input_and_output() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main([])

    assert exc_info.value.code == 2
