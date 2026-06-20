import sys
import pathogenprofiler as pp
import argparse
from pathogenprofiler.models import BamQC, SpeciesPrediction, DrGene, SequenceQC
from typing import List
import logging
import csv

def check_for_databases(args: argparse.Namespace):
    if len(pp.list_db(args.db_dir))<1:
        sys.stderr.write('No databases found... please run `ntm-profiler update_db`\n')
        quit(1)


def get_species(args: argparse.Namespace) -> SpeciesPrediction:
    if args.resistance_db:
        if args.no_species:
            return pp.set_species(args)
        else:
            return pp.get_species_prediction(args)
    else:
        return pp.get_species_prediction(args)



def summarise_sourmash_hits(sourmash_hits):
    species = []
    for hit in sourmash_hits:
        if hit["species"] not in species:
            species.append(hit["species"])
    return ";".join(species)


def merge_sourmash_species(sourmash_hits: SpeciesPrediction) -> None:
    species_detected = set(t.species for t in sourmash_hits.taxa)
    species_objects = []
    if len(sourmash_hits.taxa) == 0:
        return

    for species in species_detected:
        hits = [t for t in sourmash_hits.taxa if t.species == species]
        hits = sorted(hits,key=lambda x: x.abundance,reverse=True)
        species_objects.append(hits[0])

    total_abundance = sum([s.abundance for s in species_objects])
    for s in species_objects:
        s.relative_abundance = s.abundance/total_abundance*100
    sourmash_hits.taxa = species_objects

def add_coverage_to_genes(genes: list, qc: SequenceQC):
    for gene in genes:
        if isinstance(gene,DrGene):
            # if qc is BamQC
            if isinstance(qc, BamQC):
                for target in qc.target_qc:
                    if (gene.gene_id == target.target) or (gene.gene_name == target.target):
                        gene.coverage = target.percent_depth_pass
            else:
                logging.warning(f"Cannot add coverage to {gene.gene_name} as QC is not BamQC")

def filter_low_coverage_genes(resistance_determinants: list,input_type: str,cutoff=90) -> list:
    new_list = []
    for d in resistance_determinants:
        if isinstance(d, DrGene):

            if input_type in ('fasta','bam'):
                logging.debug(f"Checking {d.gene_name} coverage: {d.coverage} against cutoff {cutoff}")
                if d.coverage<cutoff:
                    logging.debug(f"Removing {d.gene_name} coverage ({d.coverage}) is less than cutoff {cutoff}")
                    continue
        new_list.append(d)
    return new_list

def get_gene2drugs(bed_file):
    lt2drugs = {}
    for l in open(bed_file):
        row = l.strip().split()
        lt2drugs[row[4]] = row[5].split(",")
    return lt2drugs

def rv2genes(bed_file):
    #Chromosome      759310  763325  Rv0667  rpoB    rifampicin
    rv2gene = {}
    for l in open(bed_file):
        row = l.strip().split()
        rv2gene[row[3]] = row[4]
    return rv2gene

def reformat_variant_csv_file(filename: str, outfile: str) -> str:
    rows = []
    include_mutation = False

    for row in csv.DictReader(open(filename)):
        new_rows = {
            'Gene': row['Gene'],
        }
        if "Mutation" in row:
            new_rows['Mutation'] = row['Mutation']
            include_mutation = True
        info = {}
        for k,v in row.items():
            if k in ('Gene','Mutation'):
                continue
            info[k] = v
        
        info['comment'] = row.get('Comment','')
        if 'E.coli-nomenclature' in row and row['E.coli-nomenclature']!='':
            info['comment'] += f' E.coli nomenclature: {row["E.coli-nomenclature"]}.'
        if 'hain' in row and row['hain']!='' and row['hain'] in ('yes','no'):
            info['comment'] += f' Mutation present on Hain.' if {row["hain"]}=='yes' else f' Mutation absent on Hain.'
        info['comment'] = info['comment'].strip()
        if info['comment'].endswith('='):
            del info['comment']

        info_string = ";".join([f"{k.lower()}={v}" for k,v in info.items()])
        new_rows['Info'] = info_string
        
        rows.append(new_rows)


    with open(outfile, 'w') as csvfile:
        fieldnames = ['Gene','Mutation','Info'] if include_mutation else ['Gene','Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return outfile