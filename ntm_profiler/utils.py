import sys
import json
import pathogenprofiler as pp

def log(x):
    sys.stderr.write('\033[91m' + str(x) + '\033[0m' + '\n')

def test_resistance_genes(conf,results):
    resistance_genes = {}
    db = json.load(open(conf["json_db"]))
    for gene in db:
        if "functional_gene" in db[gene]:
            resistance_genes[gene] = db[gene]["functional_gene"]

    lof = ["large_deletion","frameshift_variant"]
    for var in results["variants"]:
        for csq in var["consequences"]:
            if csq["type"] in lof and csq["gene_id"] in resistance_genes:
                log(var)
                del resistance_genes[csq["gene_id"]]

    results = []
    for gene in resistance_genes:
        res = {
            "gene_id":gene,
            "annotations":resistance_genes[gene]["annotations"],
            "type":"resistance_gene_present"    
        }
        results.append(res)
    return results
