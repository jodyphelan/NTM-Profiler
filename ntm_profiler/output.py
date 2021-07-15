
import os
from .utils import filecheck
def collate_results(outfile,samples=None,directory="."):
    if samples:
        samples = [x.rstrip() for x in open(args.samples).readlines()]
    else:
        samples = [x.replace(".species.txt","") for x in os.listdir(directory) if x[-len(".species.txt"):]==".species.txt"]

    rows = []
    for s in samples:
        for l in open(filecheck(f"{directory}/{s}.species.txt")):
            pass
        rows.append(l.strip().split())

    with open(outfile,"w") as O:
        O.write("Sample\tSpecies\tCoverage\tCoverage_SD\n")
        for row in rows:
            O.write("\t".join(row)+"\n")
        
def write_speciation_results(results,outfile):
    with open(outfile,"w") as O:
        O.write("Sample\tSpecies\tCoverage\tCoverage_SD\n")
        for x in results["species"]:
            x["sample"] = results["sample_name"]
            O.write(f"%(sample)s\t%(species)s\t%(mean)s\t%(std)s\n" % x)