import sys
import json
from uuid import uuid4
import pathogenprofiler as pp

def infolog(x):
    sys.stderr.write('\033[94m' + str(x) + '\033[0m' + '\n')

def errlog(x):
    sys.stderr.write('\033[91m' + str(x) + '\033[0m' + '\n')


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
            "gene_id":gene,
            "annotations":resistance_genes[gene]["annotations"],
            "type":"resistance_gene_present"    
        }
        results.append(res)
    return results


def get_mash_hit(args):
    args.species_conf = pp.get_db(args.software_name,args.species_db)
    db_info = pp.parse_csv(args.species_conf["mash_db_info"])
    if args.read1:
        if args.read2:
            pp.run_cmd(f"cat {args.read1} {args.read2} > {args.files_prefix}.fq.gz")
            reads = f"{args.files_prefix}.fq.gz"
        else:
            reads = args.read1
        pp.run_cmd(f"mash dist -m 2 {args.species_conf['mash_db']} {reads} | sort -gk3 | head > {args.files_prefix}.mash_dist.txt")
    elif args.fasta:
        pp.run_cmd(f"mash dist {args.species_conf['mash_db']} {args.fasta} | sort -gk3 | head > {args.files_prefix}.mash_dist.txt")

    result =  {
        "prediction_method":"mash",
        "prediction":[],
        "species_db_version":args.species_conf["version"]
    }
    for l in open(f"{args.files_prefix}.mash_dist.txt"):
        row = l.strip().split()
        acc = row[0].replace("db/","").replace(".fa","")
        species = db_info[acc]["species"]
        result["prediction"].append({
            "accession":acc,
            "species":species,
            "mash-ANI":1-float(row[2])
        })
    
    return result
