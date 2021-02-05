use std::{
    collections::HashMap,
    iter::FromIterator,
};

use serde::{
    Deserialize,
    Serialize,
};

use thiserror::Error;

use rnc_core::{
    urs,
    urs_taxid,
};

use crate::normalize::utils;

use crate::normalize::ds::{
    accession::{
        AccessionVec,
        CrossReference,
        RawAccession,
    },
    basic::Basic,
    crs::{
        Crs,
        CrsVec,
    },
    feedback::{
        Feedback,
        FeedbackVec,
    },
    go_annotation::GoAnnotation,
    interacting_protein::{
        InteractingProtein,
        InteractingProteinVec,
    },
    interacting_rna::{
        InteractingRna,
        InteractingRnaVec,
    },
    precompute::{
        Precompute,
        PrecomputeSummary,
    },
    qa_status::QaStatus,
    r2dt::R2dt,
    reference::{
        Reference,
        ReferenceVec,
    },
    rfam_hit::{
        RfamHit,
        RfamHitVec,
    },
    so_tree,
};

#[derive(Error, Debug)]
pub enum NormalizationError {
    #[error("Could not ungroup {0}")]
    CountError(#[from] utils::Error),

    #[error("Could not parse {0}")]
    UrsParsingError(#[from] urs::Error),

    #[error("Could not parse {0}")]
    UrsTaxidParsingError(#[from] urs_taxid::Error),
}

#[derive(Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Raw {
    pub accessions: Vec<RawAccession>,
    pub base: Basic,
    pub crs: Vec<Crs>,
    pub feedback: Vec<Feedback>,
    pub go_annotations: Vec<GoAnnotation>,
    pub interacting_proteins: Vec<InteractingProtein>,
    pub interacting_rnas: Vec<InteractingRna>,
    pub precompute: Precompute,
    pub qa_status: QaStatus,
    pub r2dt: Option<R2dt>,
    pub references: Vec<Reference>,
    pub rfam_hits: Vec<RfamHit>,
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
pub struct Normalized {
    urs: String,
    taxid: usize,
    urs_taxid: String,
    short_urs: String,
    deleted: String,

    so_rna_type_tree: so_tree::SoTree,

    #[serde(flatten)]
    pre_summary: PrecomputeSummary,

    #[serde(flatten)]
    basic: Basic,

    // #[serde(flatten)]
    // dates: Dates,
    qa_status: QaStatus,
    secondary_structure: Option<R2dt>,

    accessions: AccessionVec,
    cross_references: Vec<CrossReference>,
    crs: CrsVec,
    feedback: FeedbackVec,
    go_annotations: Vec<GoAnnotation>,
    interacting_proteins: InteractingProteinVec,
    interacting_rnas: InteractingRnaVec,
    references: ReferenceVec,
    rfam_hits: RfamHitVec,
}

impl Raw {
    pub fn urs_taxid(&self) -> String {
        return self.base.urs_taxid.to_owned();
    }

    pub fn urs(&self) -> Result<String, urs_taxid::Error> {
        let ut: urs_taxid::UrsTaxid = self.urs_taxid().parse()?;
        let urs: urs::Urs = ut.into();
        Ok(urs.to_string())
    }

    pub fn taxid(&self) -> Result<u64, urs_taxid::Error> {
        let ut: urs_taxid::UrsTaxid = self.urs_taxid().parse()?;
        Ok(ut.taxid())
    }

    pub fn short_urs(&self) -> Result<String, urs_taxid::Error> {
        let ut: urs_taxid::UrsTaxid = self.urs_taxid().parse()?;
        let urs: urs::Urs = ut.into();
        Ok(urs.short_urs())
    }

    pub fn short_urs_taxid(&self) -> Result<String, urs_taxid::Error> {
        let ut: urs_taxid::UrsTaxid = self.urs_taxid().parse()?;
        Ok(ut.short())
    }
}

impl Normalized {
    pub fn new(
        raw: Raw,
        so_info: &HashMap<String, so_tree::SoTree>,
    ) -> Result<Self, NormalizationError> {
        let so_rna_type_tree = so_info[raw.precompute.so_rna_type()].clone();
        let pre_summary = PrecomputeSummary::from(raw.precompute);
        let base = raw.base.clone();

        let urs_taxid = base.urs_taxid.to_owned();
        let parts: Vec<&str> = urs_taxid.split("_").collect();
        let urs = parts[0].to_owned();
        let taxid = parts[1].parse::<usize>().unwrap();
        let parsed: urs_taxid::UrsTaxid = urs_taxid.parse()?;

        Ok(Self {
            urs_taxid,
            urs,
            taxid,
            short_urs: parsed.short(),
            deleted: String::from("N"),

            so_rna_type_tree,

            pre_summary,
            basic: base,
            qa_status: raw.qa_status,
            secondary_structure: raw.r2dt.into(),

            accessions: AccessionVec::from_iter(raw.accessions.clone().into_iter()),
            cross_references: raw.accessions.into_iter().map(CrossReference::from).collect(),
            crs: CrsVec::from_iter(raw.crs.clone()),
            feedback: FeedbackVec::from_iter(raw.feedback.clone()),
            go_annotations: raw.go_annotations.clone(),
            interacting_proteins: InteractingProteinVec::from_iter(
                raw.interacting_proteins.clone(),
            ),
            interacting_rnas: InteractingRnaVec::from_iter(raw.interacting_rnas.clone()),
            references: ReferenceVec::from_iter(raw.references.clone()),
            rfam_hits: RfamHitVec::from_iter(raw.rfam_hits.clone()),
        })
    }
}
