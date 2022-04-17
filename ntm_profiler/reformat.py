import pathogenprofiler as pp

def reformat_resistance_genes(results):
    for d in results["resistance_genes"]:
        d["drugs"] = d["annotations"]
        del d["annotations"]
    return results

def reformat(results,conf):
    results["variants"] = [x for x in results["variants"] if len(x["consequences"])>0]
    results["variants"] = pp.select_csq(results["variants"])
    results["variants"] = pp.dict_list_add_genes(results["variants"],conf)
    results["resistance_genes"] = pp.dict_list_add_genes(results["resistance_genes"],conf)
    results = reformat_resistance_genes(results)
    results = pp.reformat_annotations(results,conf)

    if "gene_coverage" in results["qc"]:
        results["qc"]["gene_coverage"] = pp.dict_list_add_genes(results["qc"]["gene_coverage"],conf)
    if "missing_positions" in results["qc"]:
        results["qc"]["missing_positions"] = pp.reformat_missing_genome_pos(results["qc"]["missing_positions"],conf)
    
    return results