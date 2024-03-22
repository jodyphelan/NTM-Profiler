from pathogenprofiler.models import Gene, Variant, BarcodeResult, DrGene, DrVariant, SpeciesPrediction, BamQC, FastaQC, FastqQC
from .models import SpeciesResult, ProfileResult
from typing import List, Union

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



def create_species_result(
    id: str,
    species: SpeciesPrediction,
    qc: FastqQC
) -> SpeciesResult:
    return SpeciesResult(
        id=id,
        species=species,
        qc= qc
    )



def create_resistance_result(
    id: str,
    species: SpeciesPrediction,
    genetic_elements: List[Union[Gene, Variant, DrGene, DrVariant]],
    barcode: BarcodeResult,
    qc: Union[BamQC, FastaQC],
    notes: List[str]
) -> ProfileResult:
    dr_genes, other_genes, dr_variants, other_variants, fail_variants = split_variants_on_filter(genetic_elements)
    data = {
        'id':id,
        'notes':notes,
        'dr_genes':dr_genes,
        'other_genes':other_genes,
        'dr_variants':dr_variants,
        'other_variants':other_variants,
        'fail_variants':fail_variants,
        'species':species,
        'barcode':barcode
    }
    return ProfileResult(**data, qc=qc)