use audiotags::{traits::*, Tag};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyclass(name = "Picture")]
#[derive(Debug, Clone)]
pub struct _Picture {
    #[pyo3(get)]
    data: Vec<u8>,
    #[pyo3(get)]
    mime: String,
}

#[pymethods]
impl _Picture {
    fn ext(&self) -> PyResult<String> {
        Ok(self.mime.split_once("/").unwrap().1.to_owned())
    }
}

#[pyclass(name = "Metadata")]
pub struct Metadata {
    #[pyo3(get)]
    pub title: Option<String>,
    #[pyo3(get)]
    pub artist: Option<String>,
    #[pyo3(get)]
    pub album: Option<(String, Option<_Picture>)>,
}

/// Get metadata of a music
#[pyfunction]
fn get_metadata(file: &str) -> PyResult<Metadata> {
    let tag = Tag::new().read_from_path(&file).unwrap();
    Ok(Metadata {
        title: tag.title().map(|x| x.to_owned()),
        artist: tag.artist().map(|x| x.to_owned()),
        album: tag.album().map(|album| {
            (
                album.title.to_owned(),
                album.cover.map(|cover| _Picture {
                    data: cover.data.to_owned(),
                    mime: cover.mime_type.into(),
                }),
            )
        }),
    })
}

/// A Python module implemented in Rust.
#[pymodule]
fn musicbot(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_metadata, m)?)?;
    m.add_class::<Metadata>()?;

    Ok(())
}
