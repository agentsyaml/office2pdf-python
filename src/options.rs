use std::path::PathBuf;

use office2pdf::config::{ConvertOptions, Format, PaperSize, PdfStandard, SlideRange};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyTuple};

use crate::errors::{UnsupportedFormatError, UnsupportedOptionError};

fn parse_format_value(raw: &str) -> PyResult<Format> {
    match raw.to_ascii_lowercase().as_str() {
        "docx" => Ok(Format::Docx),
        "pptx" => Ok(Format::Pptx),
        "xlsx" => Ok(Format::Xlsx),
        other => Err(PyErr::new::<UnsupportedFormatError, _>(format!(
            "unsupported format {other:?}; expected 'docx', 'pptx', or 'xlsx'",
        ))),
    }
}

pub(crate) fn parse_format(raw: &str) -> PyResult<Format> {
    parse_format_value(raw)
}

fn parse_pdf_standard(value: &str) -> PyResult<PdfStandard> {
    match value
        .to_ascii_lowercase()
        .replace(['-', '_', '/'], "")
        .as_str()
    {
        "pdfa2b" => Ok(PdfStandard::PdfA2b),
        other => Err(PyErr::new::<UnsupportedOptionError, _>(format!(
            "unsupported pdf_standard {other:?}; expected 'pdf/a-2b'",
        ))),
    }
}

fn parse_sheet_names(value: &Bound<'_, PyAny>) -> PyResult<Vec<String>> {
    value.extract::<Vec<String>>()
}

fn parse_font_paths(value: &Bound<'_, PyAny>) -> PyResult<Vec<PathBuf>> {
    let values = value.extract::<Vec<String>>()?;
    Ok(values.into_iter().map(PathBuf::from).collect())
}

fn parse_paper_size(value: &Bound<'_, PyAny>) -> PyResult<PaperSize> {
    if let Ok(raw) = value.extract::<String>() {
        return PaperSize::parse(&raw).map_err(PyErr::new::<UnsupportedOptionError, _>);
    }

    let tuple = value.downcast::<PyTuple>()?;
    if tuple.len() == 0 {
        return Err(PyErr::new::<UnsupportedOptionError, _>(
            "invalid paper_size tuple",
        ));
    }

    let kind: String = tuple.get_item(0)?.extract()?;
    match kind.as_str() {
        "Named" | "named" => {
            let size: String = tuple.get_item(1)?.extract()?;
            PaperSize::parse(&size).map_err(PyErr::new::<UnsupportedOptionError, _>)
        }
        "Custom" | "custom" => {
            let width: f64 = tuple.get_item(1)?.extract()?;
            let height: f64 = tuple.get_item(2)?.extract()?;
            if width <= 0.0 || height <= 0.0 {
                return Err(PyErr::new::<UnsupportedOptionError, _>(
                    "custom paper size dimensions must be positive",
                ));
            }
            Ok(PaperSize::Custom { width, height })
        }
        _ => Err(PyErr::new::<UnsupportedOptionError, _>(
            "unsupported paper_size variant",
        )),
    }
}

fn reject_if_present(value: Option<&Bound<'_, PyAny>>, name: &str) -> PyResult<()> {
    if let Some(value) = value {
        if value.is_none() {
            return Ok(());
        }
        return Err(PyErr::new::<UnsupportedOptionError, _>(format!(
            "{name} is not supported by upstream office2pdf 0.6",
        )));
    }
    Ok(())
}

pub(crate) fn parse_options(
    options: Option<&Bound<'_, PyDict>>,
) -> PyResult<(ConvertOptions, bool)> {
    let mut converted = ConvertOptions::default();
    let mut include_warnings = true;

    let Some(options) = options else {
        return Ok((converted, include_warnings));
    };

    let page_range = options.get_item("page_range")?;
    let memory_limit_mb = options.get_item("memory_limit_mb")?;
    reject_if_present(page_range.as_ref(), "page_range")?;
    reject_if_present(memory_limit_mb.as_ref(), "memory_limit_mb")?;

    let sheet_names = if let Some(value) = options.get_item("sheet_names")? {
        if value.is_none() {
            None
        } else {
            Some(parse_sheet_names(&value)?)
        }
    } else {
        None
    };

    let sheet_filter = if let Some(value) = options.get_item("sheet_filter")? {
        if value.is_none() {
            None
        } else {
            Some(parse_sheet_names(&value)?)
        }
    } else {
        None
    };

    if sheet_names.is_some() && sheet_filter.is_some() && sheet_names != sheet_filter {
        return Err(PyErr::new::<UnsupportedOptionError, _>(
            "sheet_names and sheet_filter are aliases and must match",
        ));
    }

    converted.sheet_names = sheet_names.or(sheet_filter);

    if let Some(value) = options.get_item("slide_range")? {
        if !value.is_none() {
            converted.slide_range = Some(
                SlideRange::parse(&value.extract::<String>()?)
                    .map_err(PyErr::new::<UnsupportedOptionError, _>)?,
            );
        }
    }

    if let Some(value) = options.get_item("pdf_standard")? {
        if !value.is_none() {
            converted.pdf_standard = Some(parse_pdf_standard(&value.extract::<String>()?)?);
        }
    }

    if let Some(value) = options.get_item("paper_size")? {
        if !value.is_none() {
            converted.paper_size = Some(parse_paper_size(&value)?);
        }
    }

    if let Some(value) = options.get_item("font_paths")? {
        if !value.is_none() {
            converted.font_paths = parse_font_paths(&value)?;
        }
    }

    if let Some(value) = options.get_item("landscape")? {
        if !value.is_none() {
            converted.landscape = Some(value.extract::<bool>()?);
        }
    }

    if let Some(value) = options.get_item("tagged")? {
        if !value.is_none() {
            converted.tagged = value.extract::<bool>()?;
        }
    }

    if let Some(value) = options.get_item("pdf_ua")? {
        if !value.is_none() {
            converted.pdf_ua = value.extract::<bool>()?;
        }
    }

    if let Some(value) = options.get_item("streaming")? {
        if !value.is_none() {
            converted.streaming = value.extract::<bool>()?;
        }
    }

    if let Some(value) = options.get_item("streaming_chunk_size")? {
        if !value.is_none() {
            converted.streaming_chunk_size = Some(value.extract::<usize>()?);
        }
    }

    if let Some(value) = options.get_item("include_warnings")? {
        if !value.is_none() {
            include_warnings = value.extract::<bool>()?;
        }
    }

    Ok((converted, include_warnings))
}
