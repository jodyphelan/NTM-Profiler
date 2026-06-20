from datetime import datetime

from pathogenprofiler import models, object_list2text
from pathogenprofiler.models import Gene, Variant, BarcodeResult, DrGene, DrVariant, Species, BamQC, FastaQC, VcfQC, FastqQC
from pydantic import BaseModel, Field
from typing import List, Optional,  Union

__model_schema_version__ = '1.2.0'

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
    data_source: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    notes: List[str] = []

class SpeciesResult(Result):
    result_type: str = 'Species'
    taxa: List[Species]
    qc_fail_taxa: List[Species]
    qc: Union[FastqQC,FastaQC]

class ProfileResult(SpeciesResult):
    result_type: str = 'Profile'
    resistance_db: dict
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