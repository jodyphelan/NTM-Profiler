from pathogenprofiler import models, object_list2text
from pathogenprofiler.models import Gene, Variant, BarcodeResult, DrGene, DrVariant, SpeciesPrediction, BamQC, FastaQC, VcfQC, FastqQC
from pydantic import BaseModel
from typing import List, Optional,  Union

__model_schema_version__ = '1.1.0'

class Pipeline(BaseModel):
    """
    A class to hold information about the NTM-Profiler pipeline
    
    Attributes
    ----------
    software_versio  : str
        NTM-Profiler version
    db_version : dict
        TB-Profiler database version
    software : List[dict]
        Software used in the pipeline
    """
    software_version: str
    species_db_version: Optional[dict]
    resistance_db_version: Optional[dict]
    software: List[dict]

class Result(BaseModel):
    schema_version: str = __model_schema_version__
    pipeline: Pipeline
    id: str

class SpeciesResult(Result):
    result_type: str = 'Species'
    species: SpeciesPrediction
    qc: Union[FastqQC,FastaQC]

class ProfileResult(SpeciesResult):
    result_type: str = 'Profile'
    resistance_db: dict
    notes: List[str] = []
    barcode: Optional[List[BarcodeResult]] = []
    dr_variants: List[DrVariant] = []
    dr_genes: List[DrGene] = []
    other_variants: List[Variant] = []
    other_genes: List[Gene] = []
    fail_variants: List[Variant] = []
    qc: Union[BamQC, FastaQC, VcfQC]
    result_type: str = 'Profile'

    def get_qc(self):
        if isinstance(self.qc, (BamQC, FastaQC)):
            text = object_list2text(l = self.qc.target_qc)
        else:
            text = "Not available for VCF input"
        return text