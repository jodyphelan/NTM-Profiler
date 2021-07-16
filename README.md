# NTM-Profiler

This repository hosts the code for **NTM-Profiler**. A tool to predict species and drug resistance from NTM WGS data.

Please beware that this tools is in alpha testing and should not yet be considered for production use. If you would like to get involved and help out with testing or development please drop me a line through the issues tab.

## Installation

Installation is available through conda:

```
conda install -c bioconda ntm-profiler
```
## Running

### Predicting species

NTM-Profiler species prediciton is currently available to run on fastq data with at least one read file to be supplied. The output is a txt file with the species prediction.

```
ntm-profiler speciate -1 /path/to/my/reads_1.fastq.gz -2 /path/to/my/reads_2.fastq.gz -p my_sample_name
```

## How it works?

### Species prediction
Species prediction is performed by looking for pre-detemined kmers in read files which belong to a specific species.

