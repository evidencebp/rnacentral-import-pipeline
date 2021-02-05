use std::{
    collections::HashSet,
    iter::FromIterator,
};

use serde::{
    Deserialize,
    Serialize,
};

#[derive(Debug, PartialEq, Eq, Serialize, Deserialize, Clone)]
pub struct RawAccession {
    pub id: usize,
    urs_taxid: String,
    accession: String,
    common_name: Option<String>,
    database: String,
    external_id: String,
    functions: Option<String>,
    gene_synonyms: Option<String>,
    genes: Option<String>,
    locus_tags: Option<String>,
    non_coding_id: Option<String>,
    notes: Option<String>,
    optional_id: Option<String>,
    organelles: Option<String>,
    parent_accession: Option<String>,
    products: Option<String>,
    species: Option<String>,
    standard_names: Option<String>,
    tax_strings: Option<String>,
}

#[derive(Debug, PartialEq, Eq, Serialize, Deserialize, Clone)]
pub struct CrossReference {
    name: String,
    external_id: String,
    optional_id: Option<String>,
    accession: String,
    non_coding_id: Option<String>,
    parent_accession: Option<String>,
}

#[derive(Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AccessionVec {
    species: HashSet<String>,
    organelles: HashSet<String>,
    tax_strings: HashSet<String>,
    functions: HashSet<String>,
    genes: HashSet<String>,
    gene_synonyms: HashSet<String>,
    common_name: HashSet<String>,
    notes: HashSet<String>,
    locus_tags: HashSet<String>,
    standard_names: HashSet<String>,
    products: HashSet<String>,
}

impl Default for AccessionVec {
    fn default() -> Self {
        Self {
            species: HashSet::new(),
            organelles: HashSet::new(),
            tax_strings: HashSet::new(),
            functions: HashSet::new(),
            genes: HashSet::new(),
            gene_synonyms: HashSet::new(),
            common_name: HashSet::new(),
            notes: HashSet::new(),
            locus_tags: HashSet::new(),
            standard_names: HashSet::new(),
            products: HashSet::new(),
        }
    }
}

impl From<RawAccession> for CrossReference {
    fn from(raw: RawAccession) -> Self {
        Self {
            name: raw.database,
            external_id: raw.external_id,
            optional_id: raw.optional_id,
            accession: raw.accession,
            non_coding_id: raw.non_coding_id,
            parent_accession: raw.parent_accession,
        }
    }
}

impl FromIterator<RawAccession> for AccessionVec {
    fn from_iter<I: IntoIterator<Item = RawAccession>>(iter: I) -> Self {
        let mut a = AccessionVec::default();

        for i in iter {
            a.species.extend(i.species.into_iter().filter(|s| !s.is_empty()));
            a.tax_strings.extend(i.tax_strings.into_iter().filter(|t| !t.is_empty()));
            a.organelles.extend(i.organelles.clone());
            a.functions.extend(i.functions.into_iter());
            a.genes.extend(i.genes.into_iter());
            a.common_name.extend(i.common_name.into_iter());
            a.notes.extend(i.notes.into_iter());
            a.locus_tags.extend(i.locus_tags.into_iter());
            a.standard_names.extend(i.standard_names.into_iter());
            a.products.extend(i.products.into_iter());

            for synonyms in i.gene_synonyms.into_iter() {
                if synonyms.contains(";") {
                    a.gene_synonyms
                        .extend(synonyms.split(";").map(|p| p.trim()).map(str::to_string))
                } else if synonyms.contains(",") {
                    a.gene_synonyms
                        .extend(synonyms.split(",").map(|p| p.trim()).map(str::to_string))
                } else {
                    a.gene_synonyms.insert(synonyms);
                }
            }
        }

        a
    }
}
