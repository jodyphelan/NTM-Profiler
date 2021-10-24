import pathogenprofiler as pp
from datetime import datetime 
import shutil
import json
import sys
import os

def get_resistance_db(library_path,fcheck=True,onlyfiles=False):
    if "/" not in library_path and not os.path.isfile (library_path+".gff"):
        library_path = "%s/share/ntm_profiler/%s" % (sys.base_prefix,library_path)    
    files = {"gff":".gff","ref":".fasta","bed":".bed","json_db":".dr.json","version":".version.json","variables":".variables.json"}
    conf = {}
    for key in files:
        if fcheck:
            sys.stderr.write("Using %s file: %s\n" % (key,library_path+files[key]))
            conf[key] = pp.filecheck(library_path+files[key])
            if "json" in files[key]:
                conf.update(json.load(open(conf[key])))
        else:
            conf[key] = library_path+files[key]
    return conf

def get_species_db(library_path,fcheck=True):
    if "/" not in library_path and not os.path.isfile (library_path+".kmers.txt"):
        library_path = "%s/share/ntm_profiler/%s" % (sys.base_prefix,library_path)    
    files = {"kmers":".kmers.txt","version":".version.json"}
    conf = {}
    for key in files:
        if fcheck:
            sys.stderr.write("Using %s file: %s\n" % (key,library_path+files[key]))
            conf[key] = pp.filecheck(library_path+files[key])
            if "json" in files[key]:
                conf.update(json.load(open(conf[key])))
        else:
            conf[key] = library_path+files[key]
    return conf


def create_species_db(args):
    version = {"name":args.prefix}
    if not args.db_name:
        for l in pp.cmd_out("git log | head -4"):
            row = l.strip().split()
            if row == []: continue
            version[row[0].replace(":","")] = " ".join(row[1:])
        version["commit"] = version["commit"][:7]
    else:
        version["Date"] = str(datetime.now()) if not args.db_date else args.db_date
        version["name"] = args.db_name if args.db_name else "NA"
        version["commit"] = args.db_commit if args.db_name else "NA"
        version["Author"] = args.db_author if args.db_author else "NA"

    shutil.copy(args.kmers,args.prefix+".kmers.txt")
    json.dump(version,open(args.prefix+".version.json","w"))


def load_species_db(args):
    if not os.path.isdir("%s/share/ntm_profiler" % (sys.base_prefix)):
        os.mkdir("%s/share/ntm_profiler" % (sys.base_prefix))
    library_path = "%s/share/ntm_profiler/" % (sys.base_prefix)    
    
    files = get_species_db(args.prefix,fcheck=False)
    for f in files:
        shutil.copy(files[f],library_path+files[f].split("/")[-1])


def load_resistance_db(args):
    if not os.path.isdir("%s/share/ntm_profiler" % (sys.base_prefix)):
        os.mkdir("%s/share/ntm_profiler" % (sys.base_prefix))
    library_path = "%s/share/ntm_profiler/" % (sys.base_prefix)    
    
    files = get_resistance_db(args.prefix,fcheck=False,onlyfiles = True)
    for f in files:
        shutil.copy(files[f],library_path+files[f].split("/")[-1])
