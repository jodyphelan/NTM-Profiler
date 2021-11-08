# NTM-Profiler

This repository hosts the code for **NTM-Profiler**. A tool to predict species and drug resistance from NTM WGS data.

Please beware that this tools is in alpha testing and should not yet be considered for production use. If you would like to get involved and help out with testing or development please drop me a line through the issues tab.

## Installation

Installation is available through conda:

```
conda install -c bioconda ntm-profiler=0.1.1
```
## Running

### Predicting species

NTM-Profiler species prediciton is currently available to run on fastq data with at least one read file to be supplied. The output is a txt file with the species prediction.

```
ntm-profiler profile -1 /path/to/my/reads_1.fastq.gz -2 /path/to/my/reads_2.fastq.gz -p my_sample_name
```

## How it works?

### Species prediction
Species prediction is performed by looking for pre-detemined kmers in read files which belong to a specific species. 

### Resistance prediction
Resistance prediction is performed by aligning the read data to a species-specific reference genome and looking for resistance associated genes and variants. The reference and resistance database is stored in the [ntmdb github repo](https://github.com/jodyphelan/ntmdb). At the moment resistance prediction is available for:

* _Mycobacteroides abscessus subsp. abscessus_
* _Mycobacteroides abscessus subsp. bolletii_
* _Mycobacteroides abscessus subsp. massiliense_

If you would like to suggest another organism please leave a comment in [this thread](https://github.com/jodyphelan/NTM-Profiler/discussions/6).
