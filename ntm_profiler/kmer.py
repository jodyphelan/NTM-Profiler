import os
from pathogenprofiler import run_cmd, revcom
import statistics as stats
from tqdm import tqdm
from uuid import uuid4
from .utils import log 

def get_canonical_kmer(kmer):
    t = {"A":"1","C":"2","T":"3","G":"4"}
    rkmer = revcom(kmer)
    nkmer = int("".join([t[x] for x in list(kmer)]))
    nrkmer = int("".join([t[x] for x in list(rkmer)]))
    return kmer if nkmer<nrkmer else rkmer


def check_for_kmers(kmer_list_file,read1,read2=None,threads=1):

    kmer_dict = {}
    for l in open(kmer_list_file):
        row  = l.strip().split("\t")
        kmer_dict[get_canonical_kmer(row[0])] = row[1]


    tmp = str(uuid4())
    fastq_files = f"-file {read1}"
    if read2:
        fastq_files = fastq_files + f",{read2}"
    run_cmd("dsk %s -out %s -nb-cores %s" % (fastq_files,tmp,threads))
    run_cmd("dsk2ascii -file %s.h5 -out %s.kmers.txt" % (tmp,tmp))

    file_kmers = {}
    for l in tqdm(open(tmp+".kmers.txt")):
        row = l.strip().split()
        if row[0] in kmer_dict:
            file_kmers[row[0]] = int(row[1])

    os.remove("%s.h5" % tmp)
    os.remove("%s.kmers.txt" % tmp)

    kmer_support = []
    species_set = set()
    for kmer,species in kmer_dict.items():
        num = file_kmers.get(kmer,0)
        kmer_support.append({"kmer":kmer,"species":species,"num":num})
        species_set.add(species)

    species_support = []
    for s in species_set:
        support = [x["num"] for x in kmer_support if x["species"]==s]
        if len([x for x in support if x!=0])<len(support)/2:
            continue
        mean = stats.mean(support)
        std = stats.stdev(support)
        species_support.append({"species":s,"mean":mean,"std":std})

    return species_support


