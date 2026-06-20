from pathogenprofiler.models import Gene, Variant, BarcodeResult, DrGene, DrVariant, SpeciesPrediction, BamQC, FastaQC, FastqQC
from .models import SpeciesResult, ProfileResult, Pipeline
from typing import List, Union
import argparse
from pathogenprofiler.utils import get_software_used
from collections import defaultdict
import csv

def split_variants_on_filter(elements):
    dr_genes = []
    other_genes = []
    dr_variants = []
    other_variants = []
    fail_variants = []
    for e in elements:
        if isinstance(e, (Variant,DrVariant)):
            if e.filter.upper() != "PASS":
                fail_variants.append(e)
            else:
                if isinstance(e, DrVariant):
                    dr_variants.append(e)
                else:
                    other_variants.append(e)
        elif isinstance(e, (Gene,DrGene)):
            if isinstance(e, DrGene):
                dr_genes.append(e)
            else:
                other_genes.append(e)
    return dr_genes, other_genes, dr_variants, other_variants, fail_variants


def get_pipeline_object(args: argparse.Namespace) -> Pipeline:
    return Pipeline(
        software_version=args.software_version,
        species_db_version=args.species_conf['version'] if args.species_conf else None,
        resistance_db_version=args.conf['version'] if args.conf else None,
        software=get_software_used()
    )

def create_species_result(
    args: argparse.Namespace,
    id: str,
    species: SpeciesPrediction,
    qc: FastqQC
) -> SpeciesResult:
    add_complex_info(args,species)
    pipeline = get_pipeline_object(args)
    return SpeciesResult(
        id=id,
        data_source=args.data_source,
        taxa=species.taxa,
        qc_fail_taxa=species.qc_fail_taxa,
        qc= qc,
        pipeline=pipeline
    )

def add_complex_info(
    args: argparse.Namespace,
    species: SpeciesPrediction,
) -> None:
    notes = {}
    if args.species_conf and 'taxonomy_info' in args.species_conf:
        for row in csv.DictReader(open(args.species_conf['taxonomy_info'],encoding='utf-8-sig')):
            notes[row['species']] = row['complex']

    for t in species.taxa:
        if t.species in notes:
            t.notes.append(f"{t.species} is a member of the {notes[t.species]}")


        

def create_resistance_result(
    args: argparse.Namespace,
    id: str,
    species: SpeciesPrediction,
    genetic_elements: List[Union[Gene, Variant, DrGene, DrVariant]],
    barcode: BarcodeResult,
    qc: Union[BamQC, FastaQC],
    notes: List[str],
    resistance_db: dict
) -> ProfileResult:
    add_complex_info(args,species)
    pipeline = get_pipeline_object(args)
    dr_genes, other_genes, dr_variants, other_variants, fail_variants = split_variants_on_filter(genetic_elements)
    data = {
        'id':id,
        'data_source': args.data_source,
        'resistance_db':resistance_db,
        'notes':notes,
        'dr_genes':dr_genes,
        'other_genes':other_genes,
        'dr_variants':dr_variants,
        'other_variants':other_variants,
        'fail_variants':fail_variants,
        'taxa':species.taxa,
        'qc_fail_taxa': species.qc_fail_taxa,
        'barcode':barcode,
        'pipeline':pipeline
    }
    return ProfileResult(**data, qc=qc)