import sys
import pathogenprofiler as pp
import argparse
from pathogenprofiler.models import SpeciesPrediction
from typing import List

def check_for_databases(args: argparse.Namespace):
    if len(pp.list_db(args.db_dir))<1:
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


def merge_sourmash_species(sourmash_hits: SpeciesPrediction) -> None:
    species_detected = set(s.species for s in sourmash_hits.species)
    species_objects = []
    if 'abundance' not in sourmash_hits.species[0].prediction_info:
        return 
    for species in species_detected:
        hits = [s for s in sourmash_hits.species if s.species == species]
        hits = sorted(hits,key=lambda x: x.prediction_info['abundance'],reverse=True)
        species_objects.append(hits[0])
        
    total_abundance = sum([s.prediction_info['abundance'] for s in species_objects])
    for s in species_objects:
        s.prediction_info['relative_abundance'] = s.prediction_info['abundance']/total_abundance*100
    sourmash_hits.species = species_objects

