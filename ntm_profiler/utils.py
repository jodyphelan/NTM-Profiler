import sys
import json
from uuid import uuid4
import pathogenprofiler as pp
import argparse
from pathogenprofiler.models import SpeciesPrediction

def check_for_databases(args: argparse.Namespace):
    if len(pp.list_db(args.software_name))<1:
        sys.stderr.write('No databases found... please run `ntm-profiler update_db`\n')
        quit(1)


def get_species(args: argparse.Namespace) -> SpeciesPrediction:
    if args.resistance_db:
        return pp.set_species(args)
    else:
        return pp.get_sourmash_species_prediction(args)



def summarise_sourmash_hits(sourmash_hits):
    species = []
    for hit in sourmash_hits:
        if hit["species"] not in species:
            species.append(hit["species"])
    return ";".join(species)

# def consolidate_species_predictions(kmer_prediction, sourmash_prediction):
#     filtered_sourmash_prediction = [d for d in sourmash_prediction if d["ani"]>95]
#     if len(kmer_prediction)>1:
#         return None
#     elif len(kmer_prediction)>0 and len(filtered_sourmash_prediction)>0:
#         if kmer_prediction[0]["species"]==filtered_sourmash_prediction[0]["species"]:
#             return kmer_prediction[0]["species"]
#         else:
#             return None
#     elif len(filtered_sourmash_prediction)>0:
#         return filtered_sourmash_prediction[0]["species"]
#     elif len(kmer_prediction)>0:
#         return kmer_prediction[0]["species"]
#     else:
#         return None