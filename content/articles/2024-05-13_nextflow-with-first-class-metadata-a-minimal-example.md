Title: Nextflow With First Class Metadata: A Minimal Example
Date: 2024-05-13
Category: commentary
tags: workflows, bioinformatics, RNAseq

I recently wrote [an article](2024-04-26_on-bioinformatics-workflow-design.html)
regarding some of my opinions on bioinformatics workflow design. I've written
workflows in several languages over the years, but at this point it seems that
[Nextflow](https://www.nextflow.io/) has become something of the de facto
industry standard. Regardless of my opinions on which workflow languages I like
best, I thought it might make a nice example to show one of my recommendations
in action for this commonly-used workflow language.

This is a deliberately simple example of an RNAseq workflow, and not really
intended as an example of production-ready code. However, it will demonstrate
one of the points that I wrote about in that article, First Class Metadata.

## First Class Metadata

What I'm referring to as first class metadata is the concept that the important
information about your data lives elsewhere in a simple format that can be
easily parsed. The filenames themselves are not the ground truth for
information about your data. Filenames are simply an identifier and a method of
linking data to metadata. Take these hypothetical files as an example:

```
RNASEQ_cell_line_A_treated_20um_replicate_1_R1.fastq.gz
RNASEQ_cell_line_A_treated_20um_replicate_1_R2.fastq.gz
RNASEQ_cell_line_A_treated_20um_replicate_2_R1.fastq.gz
RNASEQ_cell_line_A_treated_20um_replicate_2_R2.fastq.gz
RNASEQ_cell_line_A_untreated_replicate_1_R1.fastq.gz
RNASEQ_cell_line_A_untreated_replicate_1_R2.fastq.gz
RNASEQ_cell_line_A_untreated_replicate_2_R1.fastq.gz
RNASEQ_cell_line_A_untreated_replicate_2_R2.fastq.gz
```

These are clearly from an RNAseq experiment. It even says so! What else do we
know? There's other information, apparently. They're from a cell line, the
highly specific "cell_line_A," some have been treated with *something* and we
have a concentration (20 micromolar). We also have a replicate number (I hope
in your real experiments you're doing more than one replicate...) and since
these are paired end samples there is information on whethere they are read 1
or 2 of the pair.

What would first class metadata mean? Here's an example, a simple .csv (or
.tsv):

experiment_id | sample_id    | sample_number | experiment| cell_line | treatment     | replicate | mate | filename
--------------|--------------|---------------|-----------|-----------|---------------|-----------|------|---------
RNASEQ_001    | treated_20_1 | 1             | rnaseq    | A         | 20_micromolar | 1         | 1    | RNASEQ_cell_line_A_treated_20um_replicate_1_R1.fastq.gz
RNASEQ_001    | treated_20_1 | 1             | rnaseq    | A         | 20_micromolar | 1         | 2    | RNASEQ_cell_line_A_treated_20um_replicate_1_R2.fastq.gz
RNASEQ_001    | treated_20_2 | 2             | rnaseq    | A         | 20_micromolar | 2         | 1    | RNASEQ_cell_line_A_treated_20um_replicate_2_R1.fastq.gz
RNASEQ_001    | treated_20_2 | 2             | rnaseq    | A         | 20_micromolar | 2         | 2    | RNASEQ_cell_line_A_treated_20um_replicate_2_R2.fastq.gz
RNASEQ_001    | untreated_1  | 3             | rnaseq    | A         | NA            | 1         | 1    | RNASEQ_cell_line_A_untreated_replicate_1_R1.fastq.gz
RNASEQ_001    | untreated_1  | 3             | rnaseq    | A         | NA            | 1         | 2    | RNASEQ_cell_line_A_untreated_replicate_1_R2.fastq.gz
RNASEQ_001    | untreated_2  | 4             | rnaseq    | A         | NA            | 2         | 1    | RNASEQ_cell_line_A_untreated_replicate_2_R1.fastq.gz
RNASEQ_001    | untreated_2  | 4             | rnaseq    | A         | NA            | 2         | 2    | RNASEQ_cell_line_A_untreated_replicate_2_R2.fastq.gz