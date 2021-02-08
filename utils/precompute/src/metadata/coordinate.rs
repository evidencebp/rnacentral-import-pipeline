use serde::{
    Deserialize,
    Serialize,
};

#[derive(Debug, Deserialize, Serialize, PartialEq)]
pub struct Coordinate {
    #[serde(rename = "id")]
    pub urs_taxid: String,
    assembly_id: String,
    chromosome: String,
    strand: i8,
    start: usize,
    stop: usize,
}