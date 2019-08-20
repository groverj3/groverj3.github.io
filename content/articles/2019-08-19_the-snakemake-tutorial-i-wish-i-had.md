Title: The Snakemake Tutorial I Wish I Had
Date: 2019-08-19
Category: how-to
tags: bioinformatics, python, workflows, snakemake

Over the past few years the use of workflow managers in genomics and
bioinformatics has grown greatly. This is a great thing for the field and adds to
our ability to perform reproducible analyses, especially for pipelines with many
steps. These are common in bioinformatics, but prior to the use of workflow
managers they were mostly handled with BASH scripts. While a good BASH script is
perfectly acceptable much of the time they aren't very portable and don't handle
multithreading and concurrent processes without annoying hacks. For a one-off
analysis that's all fine, but what about a pipeline you need to run many times?
This is where a workflow manager really shines, especially when combined with
containers.

I decided to implement two pipelines that we use often here in the Mosher Lab as
Snakemake workflows. We work with a lot of small RNA sequencing and recently some
whole-genome bisulfite sequencing data. There are already available pipelines for
WGBS, but they seem like overkill and writing my own is a good way to learn the
ins and outs of Snakemake.

I chose Snakemake over other workflow managers due to its already frequent use in
bioinformatics workflows and my familiarity with Python. However, Nextflow also
seems like a solid option as well. I found much of the official documentation
very lacking in useful examples though. I ended up consulting numerous workflows
available on Github. The issue there is also that a lot of them are trying to do
too much IMHO. So, I figured I'd write the tutorial I wish I had been able to
find.

### Step 0 - Install Snakemake and Your Workflow's Software Dependencies

I'm assuming you're on some kind of Linux system. Though, these directions may
also work on macOS. Your first step should be to install Snakemake:

```bash
pip install --user Snakemake
```

I always recommend *not* using your system python. If you're on a non-rolling
release distribution, or on macOS it's probably super outdated. I use
[pyenv](https://github.com/pyenv/pyenv) to manage my Python installations, though
there are other options. I also **never** use `sudo` to install python packages.

The WGBS workflow consists of several steps which can be represented by this DAG
(Snakemake can make these! Neat-o!)

<center>
![Snakemake WGBS Workflow](https://github.com/groverj3/wgbs_snakemake/raw/master/dag.png)
</center>

You can boil it down to:

1. Index the reference genome with [bwa-meth](https://github.com/brentp/bwa-meth) (needed for bwa-meth alignment)
2. Index the reference genome with [samtools faidx](http://www.htslib.org/doc/faidx.html) (needed for MethylDackel)
3. Quality reporting with [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
4. Trimming adapters with [Trim Galore](https://www.bioinformatics.babraham.ac.uk/projects/trim_galore/)
5. Quality reporting on trimmed reads (FastQC again)
6. Alignment with bwa-meth
7. Sorting with [samtools sort](http://www.htslib.org/doc/samtools.html)
8. Marking PCR duplicates with [Picard Tools](https://broadinstitute.github.io/picard/)
9. Detecting bias and extracting per-cytosine percent methylation with [MethylDackel](https://github.com/dpryan79/MethylDackel)
10. Determining fold-coverage with [mosdepth](https://github.com/brentp/mosdepth) and a little [python script](https://github.com/groverj3/wgbs_snakemake/blob/master/scripts/mosdepth_to_x_coverage.py)

Not a super complicated workflow, but enough to demonstrate a read-world use of
Snakemake. A workflow that's complicated enough you don't want to run each step
separately either.

I don't expect anyone to replicate this exact workflow, but it's a useful
example.

### Step 1 - Learn Some Snakemake Basics

There are some basics to explain before I start throwing code around. Firstly,
Snakemake does **not** work you way you might think, it actually works
**backwards** from a set of **target** files through a set of **rules**. You may
think this sounds unnecessarily confusing, but there is a good reason for this.
When Snakemake begins a workflow, this ensures that (as long as you don't do
anything too weird) it will not fail for trivial reasons like files not being
generated as inputs to other rules. It creates a [directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph)
representing the workflow for *each sample* that it can match through wildcards
to your **targets**. It will use the **rules** you define in its main script
(the Snakefile) to create a path from **targets** to **inputs (samples)**. This
is backwards from the way we think, and there are workflow managers that do
*push* rather than *pull*. Each has their advantages and disadvantages.

Another key concept is that your **rules** live in a `Snakefile`, just a Python
script with extra syntax. So, you can use Python code in it! Keep this in mind,
and you can do some neat things (creating sample tables for differential
expression, etc.).

Typically, the first **rule** in a Snakefile is called "all" and this rule will
indicate the **targets** that you want to generate. This tells Snakemake to
start and use the rules to try to make them based on wildcard matching with the
inputs.

Additionally, it's good practice to include the options you'd like a user to be
able to configure in a .json or .yaml file. You can think of these files like
a python dictionary in static file form ([pickling](https://en.wikipedia.org/wiki/Serialization)).

### Step 2 - Create a Rule

Create a blank file called `Snakefile` in the directory you're using for
development and fill it with this:

```python3
# Run fastqc on the raw .fastq.gz files
rule fastqc_raw:
    input:
        'input_data/{sample}_R{mate}.fastq.gz'
    output:
        '1_fastqc_raw/{sample}_R{mate}_fastqc.html',
        '1_fastqc_raw/{sample}_R{mate}_fastqc.zip'
    params:
        out_dir = '1_fastqc_raw/'
    shell:
        'fastqc -o {params.out_dir} {input}'
```

This is the first rule in our workflow, running FastQC on the input files. In the
`{}` are **wildcards**. While they have names, they are only there for
readability right now. The only `param` we're currently passing to it is the
output directory, but this is where your options would be. Snakemake will check
whether the `input` for a rule can be made before allowing the workflow to start.
Therefore, if yur workflow starts, it *should* finish. However, we need a rule
"all" which will tell it to be run.

Add the following to the Snakefile **before** the fastqc rule:

```python3
rule all:
    input:
        expand('1_fastqc_raw/{sample}_R{mate}_fastqc.{ext}',
               sample=SAMPLES, mate=[1, 2], ext=['html', 'zip'])
```

This tells the workflow which **targets** to create. We're still missing a very
important thing though! The samples! For that, create another file,
`config.yaml`, in the same directory and add this to it:

```yaml
samples:
    - Sample1
    - Sample2
    - etc...
```

Your `samples` are yaml entries without names (you could name them if you want),
and should **not** include read pair numbers (so 1 ID for each pair). The sample
IDs should match what is in `rule all` in place of `{sample}`. The `config.yaml`
is also where the options for your workflow steps can live, under their own
headings. Now, go back to your Snakefile and add this *above* your rules:

```python3
# Get overall workflow parameters from config.yaml
configfile: 'config.yaml'

SAMPLES = config['samples']
```

This parses the config file into a Python dictionary. Do you see how `SAMPLES` is
filled in for `{sample}` in `rule all` which then creates a **target** which can
be generated by `rule fastqc_raw`. It's kind of a mind-bender at first, but it 
all fits together.

Save all these files and include some test data in a subdirectory called
"input_data".

### Step 2 - Running Your First Rules

I copied one sample to my `input_data` directory and added it to the .yaml file:

```yaml
samples:
    - JWG3_2_2
```

Now run the workflow from the directory you're developing in with
`snakemake --cores #`:

```bash
[groverj3@x1-carbon snakemake_test]$ snakemake --cores 2
Building DAG of jobs...
Using shell: /usr/bin/bash
Provided cores: 2
Rules claiming more threads will be scaled down.
Job counts:
        count   jobs
        1       all
        2       fastqc_raw
        3

[Mon Aug 19 23:30:46 2019]
rule fastqc_raw:
    input: input_data/JWG3_2_2_R2.fastq.gz
    output: 1_fastqc_raw/JWG3_2_2_R2_fastqc.html, 1_fastqc_raw/JWG3_2_2_R2_fastqc.zip
    jobid: 2
    wildcards: sample=JWG3_2_2, mate=2


[Mon Aug 19 23:30:46 2019]
rule fastqc_raw:
    input: input_data/JWG3_2_2_R1.fastq.gz
    output: 1_fastqc_raw/JWG3_2_2_R1_fastqc.html, 1_fastqc_raw/JWG3_2_2_R1_fastqc.zip
    jobid: 1
    wildcards: sample=JWG3_2_2, mate=1

Started analysis of JWG3_2_2_R1.fastq.gzStarted analysis of JWG3_2_2_R2.fastq.gz

```

I ran it with `--cores 2`, but I did not include a `threads` parameter to the
rule in addition in `input`, `output`, `params`, and `shell`. So, it only thinks
the `rule fastqc_raw` requires one processor. This means it will parallelize
samples through that rule up to the maximum you give it at run-time! This is
handy. Do you see now how this is better than a bash script? It intelligently
replaces processes that can be run in parallel, but if you specify a number of
`threads` for the rule it will wait until those cores are available.

Let's add a few more rules.

### Step 3 - Add Rules

I'm going to add a bunch of rules. Don't freak out. Our `Snakefile` now looks
like this:

```python3
# Get overall workflow parameters from config.yaml
configfile: 'config.yaml'

SAMPLES = config['samples']
REFERENCE_GENOME = config['reference_genome']

rule all:
    input:
        expand('3_bwameth_aligned/{sample}.bam',
               sample=SAMPLES),
        expand('2_trim_galore/{sample}_R{mate}_val_{mate}_fastqc.{ext}',
               sample=SAMPLES, mate=[1, 2], ext=['html', 'zip'])


# Index the reference genome
# ancient() will assume the reference is older than output files if they exist
rule bwameth_index:
    input:
        ancient(REFERENCE_GENOME)
    output:
        REFERENCE_GENOME + '.bwameth.c2t',
        REFERENCE_GENOME + '.bwameth.c2t.amb',
        REFERENCE_GENOME + '.bwameth.c2t.ann',
        REFERENCE_GENOME + '.bwameth.c2t.bwt',
        REFERENCE_GENOME + '.bwameth.c2t.pac',
        REFERENCE_GENOME + '.bwameth.c2t.sa'
    params:
        bwameth_path = config['paths']['bwameth_path'],
    shell:
        '{params.bwameth_path} index {input}'
        
        
# Run fastqc on the raw .fastq.gz files
rule fastqc_raw:
    input:
        'input_data/{sample}_R{mate}.fastq.gz'
    output:
        '1_fastqc_raw/{sample}_R{mate}_fastqc.html',
        '1_fastqc_raw/{sample}_R{mate}_fastqc.zip'
    params:
        fastqc_path = config['paths']['fastqc_path'],
        out_dir = '1_fastqc_raw/'
    shell:
        '{params.fastqc_path} -o {params.out_dir} {input}'


# Trim the read pairs
rule trim_galore:
    input:
        '1_fastqc_raw/{sample}_R1_fastqc.html',
        '1_fastqc_raw/{sample}_R1_fastqc.zip',
        '1_fastqc_raw/{sample}_R2_fastqc.html',
        '1_fastqc_raw/{sample}_R2_fastqc.zip',
        R1 = 'input_data/{sample}_R1.fastq.gz',
        R2 = 'input_data/{sample}_R2.fastq.gz'
    output:
        '2_trim_galore/{sample}_R1_val_1.fq.gz',
        '2_trim_galore/{sample}_R1.fastq.gz_trimming_report.txt',
        '2_trim_galore/{sample}_R2_val_2.fq.gz',
        '2_trim_galore/{sample}_R2.fastq.gz_trimming_report.txt'
    params:
        adapter_seq = config['trim_galore']['adapter_seq'],
        out_dir = '2_trim_galore',
        trim_galore_path = config['paths']['trim_galore_path']
    shell:
        '''
        {params.trim_galore_path} \
        --a {params.adapter_seq} \
        --gzip \
        --trim-n \
        --quality 20 \
        --output_dir {params.out_dir} \
        --paired \
        {input.R1} {input.R2} \
        '''


# Run fastqc on the trimmmed reads
rule fastqc_trimmmed:
    input:
        '2_trim_galore/{sample}_R{mate}.fastq.gz_trimming_report.txt',
        fq_gz = '2_trim_galore/{sample}_R{mate}_val_{mate}.fq.gz'
    output:
        '2_trim_galore/{sample}_R{mate}_val_{mate}_fastqc.html',
        '2_trim_galore/{sample}_R{mate}_val_{mate}_fastqc.zip'
    params:
        fastqc_path = config['paths']['fastqc_path'],
        out_dir = '2_trim_galore/'
    shell:
        '{params.fastqc_path} -o {params.out_dir} {input.fq_gz}'


# Align to the reference
rule bwameth_align:
    input:
        {rules.bwameth_index.output},
        R1 = '2_trim_galore/{sample}_R1_val_1.fq.gz',
        R2 = '2_trim_galore/{sample}_R2_val_2.fq.gz'
    output:
        '3_bwameth_aligned/{sample}.bam'
    log:
        '3_bwameth_aligned/{sample}.bwameth.log'
    threads:
        config['bwameth']['threads']
    params:
        bwameth_path = config['paths']['bwameth_path'],
        genome = REFERENCE_GENOME
    shell:
        '''
        {params.bwameth_path} \
        -t {threads} \
        --reference {params.genome} \
        {input.R1} {input.R2} \
        2> {log} \
        | samtools view -b - \
        > {output}
        '''
```

And the `config.yaml` looks like this:

```yaml
samples:
    - JWG3_2_2_
    # Samples should be reported by ID rather than filenames, and exclude the
    # trailing "R1" and "R2", one sample ID per pair. If samples are supplied as
    # separate .fastq.gz files within each pair concatenate them to a single R1 and
    # R2 file prior to running.

reference_genome:
    reference_genome/ref_genome.fasta
    # Path to reference genome here with .fasta extension


# Options for individual workflow steps
# Configure threads for each step as desired, this is a sane starting point

trim_galore:
    adapter_seq : AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC
    quality : 20
    
 bwameth:
    threads : 10   


# Paths to individual tools
# You probably don't need to change this unless programs are not in your $PATH

paths:
  fastqc_path : fastqc
  trim_galore_path : trim_galore
  bwameth_path : bwameth.py
```


That's a lot to take in, so a few words of explanation are in order. I have moved
paths for the individual programs toa section in the config file. This is to help
with potential portability problems. On some server you may have tools installed
in directories outside your `$PATH`. They are pre-filled with just the tool
name, so they work fine when programs are executable from a command prompt but
this allows configuration (it's also at the bottom of the file because most users
shouldn't have to change it). I also now have a section for options for each
tool that's run. Which you can pull out of the dictionary made from the
`config.yaml` in each step's `params`. I've also allocated 10 threads to the
alignment step. This means it won't run if there aren't 10 threads available due
to other rules running more than 10 concurrent processes.

There are also multiple **targets** now. This is because the output from 
`rule fastqc_trimmed` is not used as input to another rule. Unless you explicitly
tell Snakemake to run that rule to generate its **target** it will not run and
you will get very annoyed.

It's a lot to take in, but this is essentially a usable workflow.

### Step 4 - Wrapping Up + A Few Tips

You can now add **rules** to your heart's content. Keep in mind though, you need
to change your **targets**! Otherwise, it won't run your new rules :(.

Also, you're probably wondering what happens when you don't actually have enough
CPUs to run that rule with 10 threads. Just change the `--cores` argument at
run-time to a lower number. It will reduce that rule's `threads` to the number
specified at run-time.

Another thing to consider if that Snakemake has the ability to work with HPC job
submission frameworks like SLURM and PBS. Though, it's not really that difficult
to include `snakemake --cores #` in a normal .pbs script. It also plays nice with
containers (Docker and Singularity). So, if you package up your software in one
you have automation and deployability all-in-one!

If you're curious what the full workflow looks like then [check it out!](https://github.com/groverj3/wgbs_snakemake)
