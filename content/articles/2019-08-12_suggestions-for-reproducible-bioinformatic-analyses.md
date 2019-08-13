Title: Suggestions for Reproducible Bioinformatic Analyses
Date: 2019-08-09
Category: commentary 
tags: bioinformatics, thoughts, workflows

Bioinformatic analyses often require lengthy workflows or pipleines, where the
output of program A feeds into program B, and so on. These programs may also not
output their results in a format which is convenient to use in the subsequent
steps, requiring writing a conversion script, or piping its output through yet
another program. This means that something as simple as running a differential
expression experiment still requires several steps. If you aren't careful this
can result in an incredibly messy filesystem. Worse, you may not remember which
programs or scripts were run on each file, and with which options. This is a huge
issue out there and likely a good reason why it's so hard to reproduce results
even when the same underlying data is used. Additionally, you'll inevitably need
to spend time doing iterative analysis. This also needs to be documented and
reproducible.

In this post I'll be explaining a few methods that we can use organize this
situation before it drives you or your coworkers mad. Depending, of course, on
the level of automation and reproucibility required of the workflow.

### Suggestion 1: Interactive Terminal Sessions Are For Development **Only**

There is most definitely a time and a place for testing things out in your
terminal. When you're learning to use a new program, needing to check the
`--help` or `man` pages, figuring out how to glue together programs A and B, etc.
However, in-depth analyses for publication should not be done in this manner.

This is because after running your analysis you may have absolutely no record of
what was run! Of course, some (but, criticall, not all!) programs will export a
log file. However, not all do. You can quickly end up in a situation where you
have no idea which script was run on which file. So, reserve the interactive
terminal sessions for those use cases above.

### Suggestion 2: Interactive Data Manipulation Should Be Performed in R or Jupyter Notebooks

Don't use Excel. I repeat, don't use Excel.

Ok, Excel has its uses. However, if you're doing complex data analysis
it's very easy to get to the scale that you'll regret using Excel quickly.
Luckily the *entire* [https://www.r-project.org/](R programming language) was 
designed for this, and [Python](https://www.python.org/) with
[Pandas](https://pandas.pydata.org/index.html) provides some similar tools. In
addition to scale, you also have no real record of what was done in an Excel
workbook. When you combine R or Python with computational notebooks you can run
code, and see the direct output of that code below it. This tracks everything
that you've run and its outputs.

Even though I do most of my interactive analysis and figure-making in R, I still
prefer Jupyter Notebooks over R Notebooks. This is because they're more widely
used, and Jupyter is extensible to multiple languages. Installing the
[R Kernel](https://irkernel.github.io/) is very simple.

### Suggestion 3: Single-run Pipelines Should be Automated With Shell Scripts

When you write a one-off pipeline it should still be automated with a script.
This enables reproducibility. In a perfect world you'd list the version of each
piece of software in the pipeline as well. This could result in a single shell
script file, or separate ones for each step. You may not know the next step
a-priori. These shell scripts should clearly indicate the date of creation and
the script's purpose. This is a simple example for one step in a single-use
pipeline:

```shell
#!/usr/bin/env bash

# Author: Jeffrey Grover
# Date: 2019-07-24
# Purpose: Extract reads over small RNA loci groups with bedtools intersect

# Use bedtools intersect and pipe to bam2fq

align_dir="~/large_data/2019-06-28_aligned_reads"

for bed_file in ./srna_groups/*.bed; do

    bed_filename=$(basename $bed_file)
    out_dir=${bed_filename%.bed}_reads
    mkdir "./$out_dir"

    for bamfile in ${align_dir}/*.bam; do
    
        bamfile_name=$(basename $bamfile)

        bedtools intersect \
                -ubam \
                -a "$bamfile" \
                -b "$srna_file" \
            | samtools bam2fq -n - > "./$out_dir/$bamfile_name.fq"
    done

    pigz -p 10 ./$out_dir/*.fq
done
```

I work with a lot of small RNA sequencing, and I recently needed to extract reads
from several different groups of small RNA loci I'd defined. It's relatively
simple to use `bedtools intersect` with your interesting loci as a .bed file and
pipe that output to `samtools bam2fq`. This isn't the kind of thing that's a
standard analysis I need to do and it's not very long. Therefore, to enable it to
be reproducible writing a quick shell script like this is the way to go. The
comment lines also carry enough information to tell someone what it does.

### Suggestion 4: Long Pipelines Should Have a **W i d e** Directory Structure

What does this mean? It means this:

```shell
[groverj3@x1-carbon wgbs_snakemake]$ ls
1_fastqc_raw                4_methyldackel_mbias    config.yaml  README.md         Snakefile
2_trim_galore               5_methyldackel_extract  input_data   reference_genome  temp_data
3_aligned_sorted_markdupes  6_mosdepth              LICENSE      scripts
```

and not this:

```shell
wgbs_snakemake/1_fastqc_raw/2_trim_galore/3_aligned_sorted_markdupes/4_methyldackel_mbias/5_methyldackel_extract/6_mosdepth
```

This makes navigating your directory structure much less of a pain. Especially
when a pipeline is several steps long.

### Suggestion 5: Automate Often-run Pipelines With Workflow Managers

If there is a particular pipeline that you run frequently then consider using a
workflow manager. Options include:

1. [snakemake](https://snakemake.readthedocs.io/en/stable/)
2. [Nextflow](https://www.nextflow.io/)
3. [scipipe](http://scipipe.org/)
4. [SciLuigi](https://github.com/pharmbio/sciluigi)

My vote goes to Snakemake with Nextflow as a close second. These tools require
some fiddling to transfer over an existing pipeline to fit their framework, but
what you gain is reproducibility and automation. Additionally, they all utilize
threading with parallel steps better than your BASH script does. They also work
with HPC job submission frameworks (SLURM, PBS, etc.) and containers.

Writing these workflows is beyond the scope of this article, but definitely worth
writing in detail about in a future one!

A word of caution: it's easy to think, "Oh, I'm only going to analyze bisulfite
sequencing this one time" only to find yourself running your workflow several
times as you acquire more data. There are also some freely available workflows
already written that you can check out!

(Shameless plug for [mine](https://github.com/groverj3/wgbs_snakemake))

### Suggestion 6: Containerize!

Wrap-up your workflow and its required software in a container for the ultimate
write once run anywhere solution. You can make a 
[Docker](https://www.docker.com/) container with your entire workflow which can
then be used on your server, or cloud computing. However, in order to run this in
an HPC environment you'll need to run it through 
[Singularity](https://sylabs.io/) instead. That's fine though! Singularity can
run Docker containers, and you'll already have one to use for cloud compute if
needed.

### Wrapping up

Hopefully you've found this informative and helpful. Next time I'll be back with
more practical examples.
