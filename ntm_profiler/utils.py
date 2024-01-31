import sys
import json
from uuid import uuid4
import pathogenprofiler as pp
import argparse
from pathogenprofiler.models import SpeciesPrediction


def get_species(args: argparse.Namespace) -> SpeciesPrediction:
    if args.resistance_db:
        return pp.set_species(args)
    else:
        return pp.get_sourmash_species_prediction(args)
    


def test_resistance_genes(conf,results):
    resistance_genes = {}
    db = conf["json_db"]
    for gene in db:
        if "functionally_normal" in db[gene]:
            resistance_genes[gene] = db[gene]["functionally_normal"]
    lof = ["large_deletion","frameshift_variant"]
    for var in results["variants"]:
        for csq in var["consequences"]:
            if "annotation" in csq:
                for ann in csq["annotation"]:
                    if "interaction" in ann:
                        if "Override" in ann["interaction"]:
                            gene,type = ann["interaction"].split("=")[1].split(":")
                            if type=="functionally_normal" and gene in resistance_genes:
                                del resistance_genes[gene]
    results = []
    for gene in resistance_genes:
        res = {
            "class":"gene",
            "gene_id":gene,
            "annotations":resistance_genes[gene]["annotations"],
            "type":"resistance_gene_present"    
        }
        results.append(res)
    return results


def summarise_sourmash_hits(sourmash_hits):
    species = []
    for hit in sourmash_hits:
        if hit["species"] not in species:
            species.append(hit["species"])
    return ";".join(species)

def consolidate_species_predictions(kmer_prediction, sourmash_prediction):
    filtered_sourmash_prediction = [d for d in sourmash_prediction if d["ani"]>95]
    if len(kmer_prediction)>1:
        return None
    elif len(kmer_prediction)>0 and len(filtered_sourmash_prediction)>0:
        if kmer_prediction[0]["species"]==filtered_sourmash_prediction[0]["species"]:
            return kmer_prediction[0]["species"]
        else:
            return None
    elif len(filtered_sourmash_prediction)>0:
        return filtered_sourmash_prediction[0]["species"]
    elif len(kmer_prediction)>0:
        return kmer_prediction[0]["species"]
    else:
        return None