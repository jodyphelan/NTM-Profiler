from pathogenprofiler import models, object_list2text
from pathogenprofiler.models import Gene, Variant, BarcodeResult, DrGene, DrVariant, SpeciesPrediction, BamQC, FastaQC, VcfQC, FastqQC
from pydantic import BaseModel
from typing import List, Optional,  Union


class Result(BaseModel):
    id: str

class SpeciesResult(Result):
    species: SpeciesPrediction
    qc: Union[FastqQC,FastaQC]

class ProfileResult(SpeciesResult):
    notes: List[str] = []
    resistance_db: dict = {}
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