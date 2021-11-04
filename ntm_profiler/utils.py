import sys
import json
import pathogenprofiler as pp

def infolog(x):
    sys.stderr.write('\033[94m' + str(x) + '\033[0m' + '\n')

def errlog(x):
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
            if "annotation" in csq:
                for ann in csq["annotation"]:
                    if "interaction" in ann:
                        if "Override" in ann["interaction"]:
                            gene,type = ann["interaction"].split("=")[1].split(":")
                            if type=="functional_gene" and gene in resistance_genes:
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
