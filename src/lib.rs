#![allow(clippy::useless_conversion)]

use std::path::PathBuf;

use office2pdf::config::{ConvertOptions, Format, PaperSize, PdfStandard, SlideRange};
use office2pdf::error::{ConvertError, ConvertMetrics, ConvertResult};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

fn parse_format(format: &str) -> PyResult<Format> {
    match format.to_ascii_lowercase().as_str() {
        "docx" => Ok(Format::Docx),
        "pptx" => Ok(Format::Pptx),
        "xlsx" => Ok(Format::Xlsx),
        other => Err(PyValueError::new_err(format!(
            "unsupported format {other:?}; expected 'docx', 'pptx', or 'xlsx'"
        ))),
    }
}

fn parse_pdf_standard(value: &str) -> PyResult<PdfStandard> {
    match value
        .to_ascii_lowercase()
        .replace(['-', '_', '/'], "")
        .as_str()
    {
        "pdfa2b" => Ok(PdfStandard::PdfA2b),
        other => Err(PyValueError::new_err(format!(
            "unsupported pdf_standard {other:?}; expected 'pdf/a-2b'"
        ))),
    }
}

fn parse_options(options: Option<&Bound<'_, PyDict>>) -> PyResult<(ConvertOptions, bool)> {
    let mut converted = ConvertOptions::default();
    let mut include_warnings = true;

    let Some(options) = options else {
        return Ok((converted, include_warnings));
    };

    if let Some(value) = options.get_item("page_range")? {
        if !value.is_none() {
            return Err(PyValueError::new_err(
                "page_range is not supported by upstream office2pdf 0.6",
            ));
        }
    }

    if let Some(value) = options.get_item("memory_limit_mb")? {
        if !value.is_none() {
            return Err(PyValueError::new_err(
                "memory_limit_mb is not supported by upstream office2pdf 0.6",
            ));
        }
    }

    if let Some(value) = options.get_item("sheet_filter")? {
        if !value.is_none() {
            converted.sheet_names = Some(value.extract::<Vec<String>>()?);
        }
    }

    if let Some(value) = options.get_item("slide_range")? {
        if !value.is_none() {
            let raw = value.extract::<String>()?;
            converted.slide_range = Some(SlideRange::parse(&raw).map_err(PyValueError::new_err)?);
        }
    }

    if let Some(value) = options.get_item("paper_size")? {
        if !value.is_none() {
            let raw = value.extract::<String>()?;
            converted.paper_size = Some(PaperSize::parse(&raw).map_err(PyValueError::new_err)?);
        }
    }

    if let Some(value) = options.get_item("landscape")? {
        if !value.is_none() {
            converted.landscape = Some(value.extract::<bool>()?);
        }
    }

    if let Some(value) = options.get_item("font_paths")? {
        if !value.is_none() {
            converted.font_paths = value
                .extract::<Vec<String>>()?
                .into_iter()
                .map(PathBuf::from)
                .collect();
        }
    }

    if let Some(value) = options.get_item("pdf_standard")? {
        if !value.is_none() {
            let raw = value.extract::<String>()?;
            converted.pdf_standard = Some(parse_pdf_standard(&raw)?);
        }
    }

    if let Some(value) = options.get_item("include_warnings")? {
        if !value.is_none() {
            include_warnings = value.extract::<bool>()?;
        }
    }

    if let Some(value) = options.get_item("streaming")? {
        if !value.is_none() {
            converted.streaming = value.extract::<bool>()?;
        }
    }

    Ok((converted, include_warnings))
}

fn convert_error(error: ConvertError) -> PyErr {
    match error {
        ConvertError::UnsupportedFormat(message) => PyValueError::new_err(message),
        ConvertError::Io(error) => PyRuntimeError::new_err(error.to_string()),
        ConvertError::Parse(message) => PyRuntimeError::new_err(format!("parse error: {message}")),
        ConvertError::Render(message) => {
            PyRuntimeError::new_err(format!("render error: {message}"))
        }
        ConvertError::UnsupportedEncryption => {
            PyRuntimeError::new_err("file is encrypted/password-protected and cannot be converted")
        }
    }
}

fn metrics_to_dict<'py>(
    py: Python<'py>,
    metrics: Option<ConvertMetrics>,
) -> PyResult<Option<Bound<'py, PyDict>>> {
    let Some(metrics) = metrics else {
        return Ok(None);
    };

    let dict = PyDict::new_bound(py);
    dict.set_item("parse_duration", metrics.parse_duration.as_secs_f64())?;
    dict.set_item("codegen_duration", metrics.codegen_duration.as_secs_f64())?;
    dict.set_item("compile_duration", metrics.compile_duration.as_secs_f64())?;
    dict.set_item("total_duration", metrics.total_duration.as_secs_f64())?;
    dict.set_item("input_size_bytes", metrics.input_size_bytes)?;
    dict.set_item("output_size_bytes", metrics.output_size_bytes)?;
    dict.set_item("page_count", metrics.page_count)?;
    Ok(Some(dict))
}

fn result_to_dict<'py>(
    py: Python<'py>,
    result: ConvertResult,
    include_warnings: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new_bound(py);
    let warnings = if include_warnings {
        result
            .warnings
            .into_iter()
            .map(|warning| warning.to_string())
            .collect::<Vec<_>>()
    } else {
        Vec::new()
    };

    dict.set_item("pdf", PyBytes::new_bound(py, &result.pdf))?;
    dict.set_item("warnings", warnings)?;
    dict.set_item("metrics", metrics_to_dict(py, result.metrics)?)?;
    Ok(dict)
}

#[pyfunction(name = "convert_bytes", signature = (data, format, options=None))]
fn py_convert_bytes<'py>(
    py: Python<'py>,
    data: &[u8],
    format: &str,
    options: Option<&Bound<'_, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let format = parse_format(format)?;
    let (options, include_warnings) = parse_options(options)?;
    let result = office2pdf::convert_bytes(data, format, &options).map_err(convert_error)?;
    result_to_dict(py, result, include_warnings)
}

#[pyfunction(name = "convert_path", signature = (path, options=None))]
fn py_convert_path<'py>(
    py: Python<'py>,
    path: PathBuf,
    options: Option<&Bound<'_, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let (options, include_warnings) = parse_options(options)?;
    let result = office2pdf::convert_with_options(path, &options).map_err(convert_error)?;
    result_to_dict(py, result, include_warnings)
}

#[pymodule]
fn _native(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    module.add_function(wrap_pyfunction!(py_convert_bytes, module)?)?;
    module.add_function(wrap_pyfunction!(py_convert_path, module)?)?;
    Ok(())
}
