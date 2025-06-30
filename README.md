# NTM-Profiler

This repository hosts the code for **NTM-Profiler**. A tool to predict species and drug resistance from NTM WGS data.

Please beware that this tools is in alpha testing and should not yet be considered for production use. If you would like to get involved and help out with testing or development please drop me a line through the issues tab.

## Installation

Installation is available through conda:

```
conda install bioconda::ntm-profiler
```

or if you have `mamba` installed:

```
mamba install bioconda::ntm-profiler
```

After installing, the relevant species and resistance databases can be downloaded by running:

```
ntm-profiler update_db
```

## Running

### Predicting species/resistance

NTM-Profiler species prediciton is currently available to run on a fastq, bam, cram, fasta or vcf data. The output is a txt file with the species prediction and if there is a resistance database then it will also output a  list of variants and if they have been associated with drug resistance.

#### Fastq data

Raw sequencing data in fastq format can been used as input using the following command. The second read is optional.

```
ntm-profiler profile -1 /path/to/my/reads_1.fastq.gz -2 /path/to/my/reads_2.fastq.gz -p my_sample_name
```

#### BAM/CRAM data

Aligned data in the form of bam or cram files can be used. Please note that the alignment files **must** have been generated with the same reference genome (even the chromosome names) as those used by `ntm-profiler` database.

```
ntm-profiler profile -a /path/to/my/bam -p my_sample_name
```

#### Fasta data

Assembled genomes or gene sequencves in fasta format can been used as input using the following command.

```
ntm-profiler profile -f /path/to/my/fasta -p my_sample_name
```

#### VCF data

Varaints stored in VCF format can been used as input using the following command. Again the chromosome names must match those in the species-specific database.

```
ntm-profiler profile --vcf /path/to/my/vcf -p my_sample_name
```

#### General options

If you have used a reference genome with different sequence names that you have used to generate a bam/cram/vcf then it is possible to align the `ntm-profiler` databases to use the same sequence names. Please go to the custom databases section to find out more.

Other useful options arguments include 
* `--threads` - sets the number of parallel threads
* `--platform` - sets the platform that was used to generate the data (default=illumina) 
* `--txt` - outputs a text based report

A full list of arguments can be found by running `ntm-profiler profile -h`

## How it works?

### Species prediction
Species prediction is performed by looking for pre-detemined kmers in read files which belong to a specific species. If no species is found using this method, mash is run using a database of all Mycobacteria sequences from GTDB to find the top 10 closest genomes.

### Resistance prediction
Resistance prediction is performed by aligning the read data to a species-specific reference genome and looking for resistance associated genes and variants. The reference and resistance database is stored in the [ntmdb github repo](https://github.com/jodyphelan/ntmdb). At the moment resistance prediction is available for:

* _Mycobacterium leprae_
* _Mycobacteroides abscessus subsp. abscessus_
* _Mycobacteroides abscessus subsp. bolletii_
* _Mycobacteroides abscessus subsp. massiliense_

If you would like to suggest another organism please leave a comment in [this thread](https://github.com/jodyphelan/NTM-Profiler/discussions/6).


## Custom databases

Custom databases can be generated for both species and resistance prediction. The simplest way is to get a copy of [ntmdb](https://github.com/jodyphelan/ntmdb) and modify to alter or add databases. 

```
git clone https://github.com/jodyphelan/ntmdb.git
```

### Species

The species database consists of a two column tab delimited file with kmers and associated aspecies. To alter the current list of kmers you can modify the `db/ntm_db.kmers.txt`. After this, navigate to the `db` directory and create the database.

```
cd db
ntm-profiler create_species_db --kmers ntm_db.kmers.txt --prefix ntmdb --load
```

The `--prefix` argument species the name of the database. `ntm-profiler` will automatically look for a database with the name **ntmdb** if no other is provided on the commandline, so it is a good idea to keep is like this. The `--load` parameter will lead to the library being automatically copied to the right locations so that `ntm-profiler` will be able to automatically detect it.

### Resistance

You can find an example of the files needed to create a resistance database by navigating to `db/Mycobacteroides_abscessus`. You will need a reference genome, gff file, a json file containing some variables and the mutations/drug associations stored in CSV format.

```
.
├── Mycobacteroides_abscessus.csv
├── genome.fasta
├── genome.gff
└── variables.json
```

The reference genome and gff giles should be named **genome.fasta** and **genome.gff** respectively. The **variables.json** file should at least contain the snpEff_database used by `ntm-profiler` to annotate mutations.

```
{
    "snpEff_db":"Mycobacterium_abscessus_atcc_19977"
}
```

The CSV file should contain the columns as shown in the example below. For more information on the format of this file see [here](https://github.com/jodyphelan/ntmdb).

| Gene | Mutation  | Drug       | Confers    | Interaction | Literature                 |
| ---- | --------- | ---------- | ---------- | ----------- | -------------------------- |
| rrl  | n.2270A>C | macrolides | resistance |             | 10.1038/s41467-021-25484-9 |
| rrl  | n.2270A>G | macrolides | resistance |             | 10.1038/s41467-021-25484-9 |

Finally, after setting these files up you can create and load the database using the following command.

```
ntm-profiler create_resistance_db --csv myfile.csv --prefix myspecies 
```

As before you can add the `--load` to automate loading of the database. Some important points to keep in mind:

* If you want ntm-profiler to automatically select the right database for resistance prediction after speciation, then the `--prefix` should match the desired species as it appears in the kmers file.
* If you are planning to use `ntm-profiler` on bam files, it is important to use `--match_ref myref.fa` to match the chromosome names used in your alignment pipeline, as it might differ with the ones used in the github repo.


## Development 

### Using latest development version

```bash
wget https://raw.githubusercontent.com/jodyphelan/NTM-Profiler/refs/heads/dev/conda/linux.explicit.txt
mamba create --name ntm-profiler-dev --file linux.explicit.txt
conda activate ntm-profiler-dev
pip install --force-reinstall git+https://github.com/jodyphelan/NTM-Profiler.git@dev
pip install --force-reinstall git+https://github.com/jodyphelan/pathogen-profiler.git@dev
# Important! remove any old folder with the name ntm-db and then run the following command to update the database
ntm-profiler update_db
```