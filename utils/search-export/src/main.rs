use std::{
    path::PathBuf,
    str::FromStr,
};
use structopt::StructOpt;

use anyhow::Result;

pub mod genes;
pub mod sequences;

#[derive(Debug)]
enum Groupable {
    Basic,
    Crs,
    Feedback,
    GoAnnotations,
    InteractingProteins,
    InteractingRnas,
    LocusInfo,
    Orfs,
    Precompute,
    QaStatus,
    R2dtHits,
    RfamHits,
}

impl FromStr for Groupable {
    type Err = String;

    fn from_str(raw: &str) -> Result<Self, Self::Err> {
        match raw {
            "basic" => Ok(Self::Basic),
            "base" => Ok(Self::Basic),
            "crs" => Ok(Self::Crs),
            "feedback" => Ok(Self::Feedback),
            "go-annotations" => Ok(Self::GoAnnotations),
            "locus-info" => Ok(Self::LocusInfo),
            "interacting-proteins" => Ok(Self::InteractingProteins),
            "interacting-rnas" => Ok(Self::InteractingRnas),
            "qa-status" => Ok(Self::QaStatus),
            "r2dt" => Ok(Self::R2dtHits),
            "r2dt-hits" => Ok(Self::R2dtHits),
            "r2dt_hits" => Ok(Self::R2dtHits),
            "rfam-hits" => Ok(Self::RfamHits),
            "rfam_hits" => Ok(Self::RfamHits),
            "orfs" => Ok(Self::Orfs),
            "precompute" => Ok(Self::Precompute),
            unknown => Err(format!("Unknown name {}", unknown)),
        }
    }
}

#[derive(Debug, StructOpt)]
#[structopt(rename_all = "kebab-case")]
enum GenesCommand {
    /// A command to filter the normalized data to only the entries that are part of some
    /// locus. This will also sort the entries by locus_id so it should be easy to
    MembersOnly {
        /// Filename to read the results from, '-' means stdin
        #[structopt(parse(from_os_str))]
        path: PathBuf,

        /// Filename to write the results to, '-' means stdout
        #[structopt(parse(from_os_str))]
        output: PathBuf,
    },

    AsXml {
        /// Filename to read the gene info from
        #[structopt(parse(from_os_str))]
        genes: PathBuf,

        /// Filename to read the selected data from
        #[structopt(parse(from_os_str))]
        members: PathBuf,

        /// Filename to write the xml data to
        #[structopt(parse(from_os_str))]
        xml_output: PathBuf,

        /// Filename to write the counts to
        #[structopt(parse(from_os_str))]
        count_output: PathBuf,
    },
}

#[derive(Debug, StructOpt)]
#[structopt(rename_all = "kebab-case")]
enum Subcommand {
    /// Merge each distinct type of metadata into single merged entries. This assumes that
    /// all files are sorted in the same way. Additionally, the xref file must have at
    /// least one entry for all possible urs_taxids.
    Group {
        /// Type of data to group
        #[structopt(case_insensitive = true)]
        data_type: Groupable,

        /// Filename to read the results from, '-' means stdin
        #[structopt(parse(from_os_str))]
        path: PathBuf,

        /// The maximum count of the entries.
        max_count: usize,

        /// Filename to write the results to, '-' means stdout
        #[structopt(parse(from_os_str))]
        output: PathBuf,
    },

    Merge {
        #[structopt(parse(from_os_str))]
        base: PathBuf,

        #[structopt(parse(from_os_str))]
        crs: PathBuf,

        #[structopt(parse(from_os_str))]
        feedback: PathBuf,

        #[structopt(parse(from_os_str))]
        go_annotations: PathBuf,

        #[structopt(parse(from_os_str))]
        interacting_proteins: PathBuf,

        #[structopt(parse(from_os_str))]
        interacting_rnas: PathBuf,

        #[structopt(parse(from_os_str))]
        locus_info: PathBuf,

        #[structopt(parse(from_os_str))]
        precompute: PathBuf,

        #[structopt(parse(from_os_str))]
        qa_status: PathBuf,

        #[structopt(parse(from_os_str))]
        r2dt_hits: PathBuf,

        #[structopt(parse(from_os_str))]
        rfam_hits: PathBuf,

        #[structopt(parse(from_os_str))]
        orfs: PathBuf,

        #[structopt(parse(from_os_str))]
        /// Filename of the SO term tree metadata.
        so_term_tree: PathBuf,

        #[structopt(parse(from_os_str))]
        /// Filename to write the results to, '-' means stdout
        output: PathBuf,
    },

    Normalize {
        #[structopt(parse(from_os_str))]
        /// Filename of the accessions
        accessions: PathBuf,

        #[structopt(parse(from_os_str))]
        /// Filename for the merged metadata
        metadata: PathBuf,

        #[structopt(parse(from_os_str))]
        /// Filename to write the results to, '-' means stdout
        output: PathBuf,
    },

    Genes {
        #[structopt(subcommand)]
        command: GenesCommand,
    },
}

#[derive(Debug, StructOpt)]
#[structopt(rename_all = "kebab-case")]
struct Opt {
    /// Set the logging option, more is more verbose.
    #[structopt(short = "v", long = "verbose", parse(from_occurrences))]
    verbose: u32,

    #[structopt(subcommand)]
    command: Subcommand,
}

fn main() -> Result<()> {
    let opt = Opt::from_args();

    let level = match opt.verbose {
        0 => simplelog::LevelFilter::Warn,
        1 => simplelog::LevelFilter::Info,
        2 => simplelog::LevelFilter::Debug,
        _ => simplelog::LevelFilter::Trace,
    };
    simplelog::TermLogger::init(
        level,
        simplelog::Config::default(),
        simplelog::TerminalMode::Stderr,
    )
    .unwrap_or_else(|_| eprintln!("Failed to create logger, ignore"));

    match opt.command {
        Subcommand::Group {
            data_type,
            path,
            max_count,
            output,
        } => match data_type {
            Groupable::Basic => sequences::basic::group(&path, max_count, &output)?,
            Groupable::Crs => sequences::crs::group(&path, max_count, &output)?,
            Groupable::Feedback => sequences::feedback::group(&path, max_count, &output)?,
            Groupable::GoAnnotations => sequences::go_annotation::group(&path, max_count, &output)?,
            Groupable::InteractingProteins => {
                sequences::interacting_protein::group(&path, max_count, &output)?
            },
            Groupable::InteractingRnas => {
                sequences::interacting_rna::group(&path, max_count, &output)?
            },
            Groupable::LocusInfo => sequences::locus::group(&path, max_count, &output)?,
            Groupable::Precompute => sequences::precompute::group(&path, max_count, &output)?,
            Groupable::QaStatus => sequences::qa_status::group(&path, max_count, &output)?,
            Groupable::R2dtHits => sequences::r2dt::group(&path, max_count, &output)?,
            Groupable::RfamHits => sequences::rfam_hit::group(&path, max_count, &output)?,
            Groupable::Orfs => sequences::orf::group(&path, max_count, &output)?,
        },
        Subcommand::Merge {
            base,
            crs,
            feedback,
            go_annotations,
            interacting_proteins,
            interacting_rnas,
            locus_info,
            precompute,
            qa_status,
            r2dt_hits,
            rfam_hits,
            orfs,
            so_term_tree,
            output,
        } => sequences::writers::write_merge(
            vec![
                base,
                crs,
                feedback,
                go_annotations,
                interacting_proteins,
                interacting_rnas,
                locus_info,
                precompute,
                qa_status,
                r2dt_hits,
                rfam_hits,
                orfs,
                so_term_tree,
            ],
            &output,
        )?,
        Subcommand::Normalize {
            accessions,
            metadata,
            output,
        } => sequences::writers::write(&accessions, &metadata, &output)?,
        Subcommand::Genes {
            command,
        } => match command {
            GenesCommand::MembersOnly {
                path,
                output,
            } => genes::writers::write_gene_members(&path, &output)?,
            GenesCommand::AsXml {
                genes,
                members,
                xml_output,
                count_output,
            } => genes::writers::write_gene_info(&genes, &members, &xml_output, &count_output)?,
        },
    }

    Ok(())
}
