use office2pdf::error::{ConvertMetrics, ConvertResult, ConvertWarning};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList};

fn convert_warning<'py>(py: Python<'py>, warning: &ConvertWarning) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new_bound(py);
    let format = warning.format().to_string();

    dict.set_item("format", &format)?;
    dict.set_item("message", warning.to_string())?;

    match warning {
        ConvertWarning::UnsupportedElement { element, .. } => {
            dict.set_item("kind", "UnsupportedElement")?;
            dict.set_item("element", element)?;
        }
        ConvertWarning::PartialElement {
            element, detail, ..
        } => {
            dict.set_item("kind", "PartialElement")?;
            dict.set_item("element", element)?;
            dict.set_item("detail", detail)?;
        }
        ConvertWarning::FallbackUsed { from, to, .. } => {
            dict.set_item("kind", "FallbackUsed")?;
            dict.set_item("from", from)?;
            dict.set_item("to", to)?;
        }
        ConvertWarning::ParseSkipped { reason, .. } => {
            dict.set_item("kind", "ParseSkipped")?;
            dict.set_item("reason", reason)?;
        }
    }

    Ok(dict)
}

fn convert_metrics<'py>(
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

pub(crate) fn convert_result_to_dict<'py>(
    py: Python<'py>,
    result: ConvertResult,
    include_warnings: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new_bound(py);
    let warnings = if include_warnings {
        result
            .warnings
            .iter()
            .map(|warning| convert_warning(py, warning))
            .collect::<PyResult<Vec<_>>>()?
    } else {
        Vec::new()
    };

    dict.set_item("pdf", PyBytes::new_bound(py, &result.pdf))?;
    dict.set_item("warnings", PyList::new_bound(py, warnings))?;
    dict.set_item("metrics", convert_metrics(py, result.metrics)?)?;
    Ok(dict)
}
