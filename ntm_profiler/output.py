
import os
from .utils import filecheck
import csv

def collate_results(outfile,samples_file=None,directory=".",sep="\t"):
    if samples_file:
        samples = [x.rstrip() for x in open(samples_file).readlines()]
    else:
        samples = [x.replace(".species.txt","") for x in os.listdir(directory) if x[-len(".species.txt"):]==".species.txt"]

    rows = []
    for s in samples:
        tmp = []
        for r in csv.DictReader(open(filecheck(f"{directory}/{s}.species.txt")),delimiter="\t"):
            tmp.append(r)
        combined_row = {"sample":s}
        for col in r:
            combined_row[col] = ";".join([str(x[col]) for x in tmp])
        rows.append(combined_row)
            

    with open(outfile,"w") as O:
        writer = csv.DictWriter(O,fieldnames = list(rows[0]),delimiter=sep)
        writer.writeheader()
        writer.writerows(rows)
        
def write_speciation_results(results,outfile):
    with open(outfile,"w") as O:
        O.write("Sample\tSpecies\tCoverage\tCoverage_SD\n")
        for x in results["species"]:
            x["sample"] = results["sample_name"]
            O.write(f"%(sample)s\t%(species)s\t%(mean)s\t%(std)s\n" % x)