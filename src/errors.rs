use office2pdf::error::ConvertError;
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;

create_exception!(_native, Office2PdfError, PyException);
create_exception!(_native, UnsupportedFormatError, Office2PdfError);
create_exception!(_native, Office2PdfIoError, Office2PdfError);
create_exception!(_native, Office2PdfParseError, Office2PdfError);
create_exception!(_native, Office2PdfRenderError, Office2PdfError);
create_exception!(_native, UnsupportedEncryptionError, Office2PdfError);
create_exception!(_native, UnsupportedOptionError, Office2PdfError);

pub(crate) fn register_exceptions(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();

    module.add("Office2PdfError", py.get_type_bound::<Office2PdfError>())?;
    module.add(
        "UnsupportedFormatError",
        py.get_type_bound::<UnsupportedFormatError>(),
    )?;
    module.add(
        "Office2PdfIoError",
        py.get_type_bound::<Office2PdfIoError>(),
    )?;
    module.add(
        "Office2PdfParseError",
        py.get_type_bound::<Office2PdfParseError>(),
    )?;
    module.add(
        "Office2PdfRenderError",
        py.get_type_bound::<Office2PdfRenderError>(),
    )?;
    module.add(
        "UnsupportedEncryptionError",
        py.get_type_bound::<UnsupportedEncryptionError>(),
    )?;
    module.add(
        "UnsupportedOptionError",
        py.get_type_bound::<UnsupportedOptionError>(),
    )?;
    Ok(())
}

pub(crate) fn convert_error(error: ConvertError) -> PyErr {
    match error {
        ConvertError::UnsupportedFormat(message) => UnsupportedFormatError::new_err(message),
        ConvertError::Io(error) => Office2PdfIoError::new_err(error.to_string()),
        ConvertError::Parse(message) => {
            Office2PdfParseError::new_err(format!("parse error: {message}"))
        }
        ConvertError::Render(message) => {
            Office2PdfRenderError::new_err(format!("render error: {message}"))
        }
        ConvertError::UnsupportedEncryption => UnsupportedEncryptionError::new_err(
            "file is encrypted/password-protected and cannot be converted",
        ),
    }
}
