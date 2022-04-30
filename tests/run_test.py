from pathogenprofiler import run_cmd
import pathogenprofiler as pp
import json
import os

example = json.load(open("ERR459870.results.json"))

if not os.path.isdir("scratch"):
    os.mkdir("scratch")
os.chdir("scratch")

def get_variants(data,type):
    return [(x["gene"],x["change"]) for x in data[type]]

def test_update_library():
    run_cmd("ntm-profiler update_db --branch leprae")

def test_fasta_profile():
    run_cmd("ntm-profiler profile -f ~/test_data/ERR459870.contigs.fa -p ERR459870_fasta -t 3 --txt --csv")
    result = json.load(open("ERR459870_fasta.results.json"))
    assert result["resistance_genes"] == example["resistance_genes"]
    assert get_variants(example,"dr_variants")== get_variants(result,"dr_variants")
    assert get_variants(example,"other_variants")== get_variants(result,"other_variants")

def test_profile():
    run_cmd("ntm-profiler profile -1 ~/test_data/ERR459870_1.fastq.gz -2 ~/test_data/ERR459870_2.fastq.gz -p ERR459870 -t 3 --txt --csv")
    result = json.load(open("ERR459870.results.json"))
    assert result == example

def test_profile_unknown():
    run_cmd("ntm-profiler profile -1 ~/test_data/DRR332975_1.fastq.gz -2 ~/test_data/DRR332975_2.fastq.gz  -p DRR332975 -t 3 --txt --csv")
    result = json.load(open("DRR332975.results.json"))
    assert len(result['mash_closest_species']['prediction']) > 0

# def test_clean():
#     os.chdir("../")
#     run_cmd("rm -r scratch")