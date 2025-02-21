
from collections import defaultdict
import os
from pathogenprofiler import filecheck
import csv
import pathogenprofiler as pp
import time
from tqdm import tqdm
import json
import jinja2
import logging
from .models import ProfileResult, SpeciesResult, Result
from typing import List, Tuple, Optional

def write_outputs(args,result: ProfileResult):
    logging.info("\nWriting outputs")
    logging.info("---------------")
    json_output = args.dir+"/"+args.prefix+".results.json"
    text_output = args.dir+"/"+args.prefix+".results.txt"
    csv_output = args.dir+"/"+args.prefix+".results.csv"
    logging.info(f"Writing json file: {json_output}")
    open(json_output,"w").write(result.model_dump_json(indent=4))

    if args.txt:
        logging.info(f"Writing text file: {text_output}")
        write_text(result,args.conf,text_output)
    if args.csv:
        logging.info(f"Writing csv file: {csv_output}")
        write_text(result,args.conf,csv_output,sep=",")

default_template = """
NTM-Profiler report
=================

The following report has been generated by NTM-Profiler.

Summary
-------
ID{{d['sep']}}{{d['id']}}
Date{{d['sep']}}{{d['date']}}

Notes
-----
{{d['notes']}}

Species report
-----------------
{{d['sourmash_species_report']}}

{%- if 'cluster_report' in d %}
Cluster report
-----------------
{{d['cluster_report']}}
{% endif %}

{% if  'dr_report' in d %}
Resistance report
-----------------
{{d['dr_report']}}

Resistance genes report
-----------------
{{d['dr_genes_report']}}

Resistance variants report
-----------------
{{d['dr_var_report']}}

Other variants report
---------------------
{{d['other_var_report']}}

Coverage report
---------------------
{{d['coverage_report']}}

Missing positions report
---------------------
{{d['missing_report']}}
{% endif %}

Analysis pipeline specifications
--------------------------------
Pipeline version{{d['sep']}}{{d['software_version']}}
Species Database version{{d['sep']}}{{d['species_db_version']}}
Resistance Database version{{d['sep']}}{{d['resistance_db_version']}}

{{d['pipeline']}}
"""
        


species_template = """
NTM-Profiler report
=================

The following report has been generated by NTM-Profiler.

Summary
-------
ID{{d['sep']}}{{d['id']}}
Date{{d['sep']}}{{d['date']}}

Species report
-----------------
{{d['sourmash_species_report']}}

Analysis pipeline specifications
--------------------------------
Pipeline version{{d['sep']}}{{d['software_version']}}
Species Database version{{d['sep']}}{{d['species_db_version']}}

{{d['pipeline']}}
"""


def load_text(text_strings: str,template: str = None,file_template: str = None):
    
    if file_template:
        template = open(file_template).read()

    t =  jinja2.Template(template)
    return t.render(d=text_strings)


def write_text(
        result: Result,
        conf: dict,
        outfile: str,
        sep: str ="\t",
        template_file: str = None
    ):
    text_strings = {}
    text_strings["id"] = result.id
    text_strings["date"] = time.ctime()
    text_strings['sourmash_species_report'] = pp.dict_list2text([d.prediction_info for d in result.species.species],mappings={"species":"Species","accession":"Accession","ani":"ANI","abundance":"Abundance","relative_abundance":"Relative abundance"},sep=sep)
    


    if isinstance(result, ProfileResult):
    
        template_string = default_template
        summary_table = pp.get_dr_summary(result.dr_variants + result.dr_genes,conf)

        text_strings["notes"] = "\n".join(result.notes)
        text_strings["dr_report"] = pp.dict_list2text(summary_table,sep=sep)
        text_strings["dr_genes_report"] = pp.object_list2text(result.dr_genes,mappings={"gene_id":"Locus Tag","gene_name":"Gene name","drugs.drug":"Drug"},sep=sep)
        text_strings["dr_var_report"] = pp.object_list2text(result.dr_variants,mappings={"pos":"Genome Position","gene_id":"Locus Tag",'gene_name':'Gene name',"type":"Variant type","change":"Change","freq":"Estimated fraction","drugs.drug":"Drug","annotation.comment":"Comment"},sep=sep)
        text_strings["other_var_report"] = pp.object_list2text(result.other_variants,mappings={"pos":"Genome Position","gene_id":"Locus Tag",'gene_name':'Gene name',"type":"Variant type","change":"Change","freq":"Estimated fraction","annotation.comment":"Comment"},sep=sep)
        text_strings['qc_fail_var_report'] = pp.object_list2text(result.fail_variants,mappings={"pos":"Genome Position","gene_id":"Locus Tag",'gene_name':'Gene name',"type":"Variant type","change":"Change","freq":"Estimated fraction","annotation.comment":"Comment"},sep=sep)
        text_strings["coverage_report"] = result.get_qc()
        text_strings['resistance_db_version'] = f'%(name)s - %(repo)s (%(commit)s:%(status)s) ' % result.pipeline.resistance_db_version

    else:
        template_string = species_template

    text_strings['software_version'] = result.pipeline.software_version
    text_strings['species_db_version'] = f'%(name)s - %(repo)s (%(commit)s:%(status)s)' % result.pipeline.species_db_version
    text_strings['pipeline'] = pp.dict_list2text(result.pipeline.software,sep=sep)

    if sep=="\t":
        text_strings["sep"] = ": "
    else:
        text_strings["sep"] = ","

    with open(outfile,"w") as O:
        O.write(load_text(text_strings,template_string,template_file))


class VariantDB:
    def __init__(self, json_db: Optional[dict] = None):
        self.samples2variants = defaultdict(set)
        self.variant2samples = defaultdict(set)
        self.variant_frequencies = {}
        self.samples = list()
        self.variant_rows = []
        if json_db:
            for gene in json_db:
                for mutation in json_db[gene]:
                        self.variant2samples[(gene,mutation)] = set()

    def add_result(self, result: ProfileResult) -> None:
        self.samples.append(result.id)
        for var in result.dr_variants + result.other_variants:
            key = (result.id,var.gene_name,var.change)
            self.variant_frequencies[key] = var.freq
            key = (var.gene_name,var.change)
            self.variant2samples[key].add(result.id)
            self.samples2variants[result.id].add(key)
            d = var.model_dump()
            d['sample'] = result.id
            self.variant_rows.append(d)
    def get_frequency(self,key: Tuple[str,str,str]) -> float:
        return self.variant_frequencies.get(key,0.0)
    def get_variant_list(self) -> List[Tuple[str,str]]:
        return list(self.variant2samples.keys())
    def write_dump(self,filename: str) -> None:
        with open(filename,"w") as O:
            fields = ["sample","gene_name","change","freq","type"]
            writer = csv.DictWriter(O,fieldnames=fields)
            writer.writeheader()
            for row in self.variant_rows:
                d = {k:row[k] for k in fields}
                writer.writerow(d)

def collate(args):
    # Get a dictionary with the database file: {"ref": "/path/to/fasta" ... etc. }
    
    if args.samples:
        samples = [x.rstrip() for x in open(args.samples).readlines()]
    else:
        samples = [x.replace(args.suffix,"") for x in os.listdir(args.dir) if x[-len(args.suffix):]==args.suffix]

    if len(samples)==0:
        pp.logging.info(f"\nNo result files found in directory '{args.dir}'. Do you need to specify '--dir'?\n")
        quit(0)

    # Loop through the sample result files    
    variant_db = VariantDB()
    rows = []
    drug_resistance_results = []
    resistance_dbs_used = set()
    for s in tqdm(samples):
        # Data has the same structure as the .result.json files
        data = json.load(open(filecheck("%s/%s%s" % (args.dir,s,args.suffix))))
        if data['result_type']=='Species':
            result = SpeciesResult(**data)
        else:
            result = ProfileResult(**data)
        row = {
            'id': s
        }
        
        # top_species_hit = result.species.species[0] if len(result.species.species)>0 else None
        if len(result.species.species)>0:
            row['species'] =  ";".join([hit.species for hit in result.species.species])
            row['closest-sequence'] = ";".join([hit.prediction_info['accession'] for hit in result.species.species])
            row['ANI'] = ";".join([str(hit.prediction_info['ani']) for hit in result.species.species])
        else:
            row['species'] =  None
            row['closest-sequence'] = None
            row['ANI'] = None
        if isinstance(result, ProfileResult):
            resistance_dbs_used.add(result.pipeline.resistance_db_version['name'])
            variant_db.add_result(result)
            row['barcode'] = ";".join([x.id for x in result.barcode]) 
            print(row['barcode'])
            for var in result.dr_variants + result.dr_genes:
                for d in var.drugs:
                    drug_resistance_results.append({
                        'id': s,
                        'drug': d['drug'],
                        'var': var.get_str(),
                    })
                    

        rows.append(row) 


    drugs = set()
    for res_db in resistance_dbs_used:
        res_db_conf = pp.get_db(args.db_dir,res_db,verbose=False)
        drugs.update(res_db_conf['drugs'])

    drugs = sorted(list(drugs))

    for row in rows:
        for drug in drugs:
            row[drug] = "; ".join([x['var'] for x in drug_resistance_results if x['id']==row['id'] and x['drug']==drug])
    
    if args.format=="txt":
        args.sep = "\t"
    else:
        args.sep = ","

    with open(args.outfile,"w") as O:
        writer = csv.DictWriter(O,fieldnames=list(rows[0]),delimiter=args.sep,extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    variant_db.write_dump(args.outfile + ".variants.csv")