Title: Nextflow With First Class Metadata: A Minimal Example
Date: 2024-05-24
Category: how-to
tags: workflows, bioinformatics, RNAseq

TLDR - Check out this github repo for the full example:
[https://github.com/groverj3/minimal_nextflow_samplesheet_example](https://github.com/groverj3/minimal_nextflow_samplesheet_example)

I recently wrote [an article](2024-04-26_on-bioinformatics-workflow-design.html)
regarding some of my opinions on bioinformatics workflow design. I've written
workflows in several languages over the years, but at this point it seems that
[Nextflow](https://www.nextflow.io/) has become something of the de facto
industry standard. I thought it might make a nice example to show one of my
recommendations in action for this commonly-used workflow language.

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
these are paired end samples there is information on whether they are read 1
or 2 of the pair.

What would first class metadata mean? Here's an example, a simple .csv (or
.tsv):

| sample_id    | experiment | cell_line | treatment     | replicate | paired_status | read1                                                   | read2                                                   |
| ------------ | ---------- | --------- | ------------- | --------- | ------------- | ------------------------------------------------------- | ------------------------------------------------------- |
| treated_20_1 | rnaseq     | A         | 20_micromolar | 1         | paired_end    | RNASEQ_cell_line_A_treated_20um_replicate_1_R1.fastq.gz | RNASEQ_cell_line_A_treated_20um_replicate_1_R2.fastq.gz |
| treated_20_2 | rnaseq     | A         | 20_micromolar | 2         | paired_end    | RNASEQ_cell_line_A_treated_20um_replicate_2_R1.fastq.gz | RNASEQ_cell_line_A_treated_20um_replicate_2_R1.fastq.gz |
| untreated_1  | rnaseq     | A         | NA            | 1         | paired_end    | RNASEQ_cell_line_A_untreated_replicate_1_R1.fastq.gz    | RNASEQ_cell_line_A_untreated_replicate_1_R2.fastq.gz    |
| untreated_2  | rnaseq     | A         | NA            | 2         | paired_end    | RNASEQ_cell_line_A_untreated_replicate_2_R1.fastq.gz    | RNASEQ_cell_line_A_untreated_replicate_2_R2.fastq.gz    |

What makes it "first class" is that this separate document, whether that's a
tabular file or something more complex like a database, is the ultimate source
of truth. The **sample** is also the fundamental unit of observations in the
table, rather than the **file**. This is apparent because both reads are listed
for a single sample, rather than each as a separate line. This means that
single-end and paired-end samples can coexist without the need to duplicate a
lot of metadata on more lines. Some sequencing protocols also create a separate
fastq for UMIs or barcodes, they could also be included as an addtitional
metadata field.

These metadata can then be parsed when executing a workflow as long as the
files are referenced in the same sample sheet. Using this paradigm it's easier 
to use sample metadata in the course of your workflow execution. Perhaps you'll
assign output file names based on the sample_id field above, or split samples
into groups based on treatment. The possibilities are myriad!

## How Does First Class Metadata Help My Nextflow Workflows?

If you've recorded your sample metadata in this fashion you can directly read
it during workflow execution. This means you're no longer forced to create
brittle code that makes assumptions about your samples based on file names.
Some of the [nf-core](https://nf-co.re/) workflows make use of these ideas.

This isn't a full-blown Nextflow tutorial, but I will demonstrate this with a
minimal example. Imagine you have a simple RNAseq workflow, just Fastqc and a
pseudoaligner like Salmon. All your sample information is contained within a
single .csv file. When you define your workflow in the `.nf` file you can
create a channel that takes your metadata sheet as an input like so:

```groovy
workflow {
    // Read samplesheet and convert to queueable channel of: sample id, paired_status, read1, read2 as a tuple
    reads_channel = channel.fromPath(params.samplesheet)
        | splitCsv(header:true)
        | map{
            // map{} applies a closure (function) to each element of a channel
            // In this case, the rows from splitCsv() are converted to a tuple based on the header 
            row -> tuple(row.sample_id, row.paired_status, file(params.input_dir + row.read1), file(params.input_dir + row.read2))
        }
    
    FASTQC(reads_channel)
    SALMON_QUANT(reads_channel)
}
```

`map{}` is an operator that applies a function to each element of a channel. In
this case, the iterator returned by splitCsv (named `row` here for clarity) is
converted to a tuple that contains sample information. This tuple is then used
as input to FASTQC and SALMON_QUANT, the only two steps (processes in
Nextflowese, which would be defined elsewhere in the .nf file) in the workflow.

The idea is you would use your main metadata database as the sample sheet, just
filtered for the samples you want to analyze.

The full example can be found here: [https://github.com/groverj3/minimal_nextflow_samplesheet_example](https://github.com/groverj3/minimal_nextflow_samplesheet_example).
I have included lots of comments to help you get started writing Nextflow, as
well as ways to procure a small test dataset. The test dataset and workflow run
in just over a minute on my laptop, excluding pulling containers, so lack of a
cluster or cloud compute environment shouldn't stand in your way for testing.

![Podman Example](https://raw.githubusercontent.com/groverj3/minimal_nextflow_samplesheet_example/main/example_execution/podman_run.png)

## Conclusion

This very simple example highlights a strategy I use when writing workflows,
and currently that means Nextflow. These ideas are transferrable to other
workflow languages as well. Personally, I am a fan of Snakemake, as it was the
first workflow language I learned, and it's implemented in Python. However,
Nextflow has become something of an industry standard, and Snakemake is more
common in academia, plus Seqera labs supports Nextflow with paid products like
the Seqera Platform (formerly known as Nextflow Tower), and there are other
bioinformatics cloud platforms that are increasingly supporting Nextflow
workflows. At the end of the day, it is a tool to help enable reproducible
analysis of your data, and we should be careful to do it in a way that
maximizes that reproducibility.

If you're interested in more advanced and/or more comprehensive Nextflow
material I can recommend the docs at [https://www.nextflow.io/docs/latest/index.html](https://www.nextflow.io/docs/latest/index.html)
and the Nextflow training material at [https://training.nextflow.io/](https://training.nextflow.io/).
There is also a lot of content you can find trawling around GitHub.