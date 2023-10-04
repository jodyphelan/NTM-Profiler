import sys
import json
from uuid import uuid4
import pathogenprofiler as pp


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


def get_sourmash_hit(args):
    args.species_conf = pp.get_db(args.software_name,args.species_db)
    if args.read1:
        if args.read2:
            fastq = pp.Fastq(args.read1,args.read2)
        else:
            fastq = pp.Fastq(args.read1)
        raw_sourmash_sig = fastq.sourmash_sketch(args.files_prefix)
        sourmash_sig = raw_sourmash_sig.filter()
    elif args.fasta:
        pp.run_cmd(f"mash dist {args.species_conf['sourmash_db']} {args.fasta} | sort -gk3 | head > {args.files_prefix}.mash_dist.txt")
        fasta = pp.Fasta(args.fasta)
        sourmash_sig = fasta.sourmash_sketch(args.files_prefix)
    elif args.bam:
        pp.run_cmd(f"samtools fastq {args.bam} > {args.files_prefix}.tmp.fastq")
        fq_file = f"{args.files_prefix}.tmp.fastq"
        fastq = pp.Fastq(fq_file)
        raw_sourmash_sig = fastq.sourmash_sketch(args.files_prefix)
        sourmash_sig = raw_sourmash_sig.filter()

    sourmash_sig = sourmash_sig.gather(args.species_conf["sourmash_db"],args.species_conf["sourmash_db_info"])
    result =  []

    if len(sourmash_sig)>0:
        result = sourmash_sig
    
    return result

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