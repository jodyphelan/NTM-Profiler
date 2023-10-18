import pathogenprofiler as pp

def reformat_resistance_genes(results):
    for d in results["resistance_genes"]:
        d["drugs"] = d["annotations"]
        del d["annotations"]
    return results

def add_subspecies(results):
    if "barcode" in results:
        subspecies_found = [d['annotation'] for d in results["barcode"] if d['annotation'].startswith("subsp.")]
        if len(subspecies_found)>0:
            subspecies_list = [results["species"]["prediction"] + " "+ d for d in subspecies_found]
            results["species"]["prediction"] = ";".join(subspecies_list)


def reformat(results,conf):
    results["variants"] = [x for x in results["variants"] if len(x["consequences"])>0]
    results["variants"] = pp.select_csq(results["variants"])
    results["variants"] = pp.dict_list_add_genes(results["variants"],conf)
    results["resistance_genes"] = pp.dict_list_add_genes(results["resistance_genes"],conf)
    results = reformat_resistance_genes(results)
    results = pp.reformat_annotations(results,conf)

    if "region_qc" in results["qc"]:
        results["qc"]["region_qc"] = pp.dict_list_add_genes(results["qc"]["region_qc"],conf,key="region")
    if "missing_positions" in results["qc"]:
        results["qc"]["missing_positions"] = pp.reformat_missing_genome_pos(results["qc"]["missing_positions"],conf)
    
    add_subspecies(results)
    return results