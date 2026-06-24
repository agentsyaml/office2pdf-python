// PyO3's #[pyfunction] expansion currently triggers this false-positive under -D warnings.
#![allow(clippy::useless_conversion)]
// PyO3 exception macros emit cfg names that stable rustc does not know about on this toolchain.
#![allow(unexpected_cfgs)]

mod errors;
mod options;
mod result;

use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pyfunction(name = "convert_bytes", signature = (data, format, options = None))]
fn convert_bytes_py<'py>(
    py: Python<'py>,
    data: &'py [u8],
    format: &'py str,
    options: Option<&'py Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let format = options::parse_format(format)?;
    let (options, include_warnings) = options::parse_options(options)?;

    let conversion =
        office2pdf::convert_bytes(data, format, &options).map_err(errors::convert_error)?;
    result::convert_result_to_dict(py, conversion, include_warnings)
}

#[pyfunction(name = "convert_path", signature = (path, options = None))]
fn convert_path_py<'py>(
    py: Python<'py>,
    path: std::path::PathBuf,
    options: Option<&'py Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyDict>> {
    let (options, include_warnings) = options::parse_options(options)?;
    let conversion =
        office2pdf::convert_with_options(path, &options).map_err(errors::convert_error)?;
    result::convert_result_to_dict(py, conversion, include_warnings)
}

#[pymodule]
fn _native(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    errors::register_exceptions(module)?;
    module.add_function(wrap_pyfunction!(convert_bytes_py, module)?)?;
    module.add_function(wrap_pyfunction!(convert_path_py, module)?)?;
    Ok(())
}
