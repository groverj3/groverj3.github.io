Title: Variations on RNAseq Workflows for DEG Analysis
Date: 2019-07-09
Category: commentary 
tags: bioinformatics, thoughts

When analyzing RNAseq you're faced with many possible analysis pipelines. The
biggest decision you need to make is what the purpose of your experiment is. I
will make the assumption that *most* of the time people want to determine which
genes are differentially expressed between two samples, genotypes, conditions,
etc. In DEG analyss you are interested in gene-level expression. This means you
are **not** interested in differential isoforms/transcripts or alternative
splicing.The absolute most simple version of this is simply having control and
experimental samples (preferably with >= 3 biological replicates each). However,
this isn't as straightforward as firing up your favorite aligner and going to
town on the data. There are other considerations.

### I Have a High Quality Annotated Reference Genome or Transcriptome

**My Reference Genome is High Quality**

1. Align reads to reference genome (STAR, HISAT2)
2. Count reads per gene (HTSeq-count, summarizeOverlaps, featurecounts)
3. DEG Analysis (DESeq2, edgeR)

This is the standard workflow that you're probably accustomed to. Note: it is
very important to use a *modern* splicing-aware aligner. Do not use bowtie. Both
STAR and HISAT2 are very fast compared to older aligners and are designed for
RNAseq. Their default options are generally appropriate for most simple
experimental designs. As a bonus, STAR can actually do step 2 itself, although
the output format is kind of clunky.

This workflow is a good general purpose one in model organisms, and nobody will
fault you for using it there. However, there are potentially better options.

**My Annotation/transcriptome is High Quality**

1. Pseudoalignment-based abundance estimation (Salmon, Kallisto)
2. Aggregate abundances per gene from transcripts (tximport)
3. DEG Analysis (DESeq2, edgeR)

This workflow may actually be better
([ref](https://f1000research.com/articles/4-1521/v2)) even if you have a
reference genome. I've always assumed that reference-genome alignment is superior
when you have a good reference, but apparently this is not necessarily the case
for the reasons detailed here.

**Pros:** very fast, potentially more accurate.

**Cons:** no .bam file is generated so you can't look at positional information
from your reads, no ability to discover new transcripts later from your
alignments.

Either of these workflows will work fine in this situation, and the better your
genome is the closer the first will likely approximate the second. Though, I now
believe that the second workflow should be the standard if your goal is purely
DEG analysis. There are still a lot of good reasons to want a .bam file, though
nothing is stopping you from aligning your reads anyway for future-use.

### My Genome/Transcriptome is Incomplete

In this case you have some deicsions to make, yet again.

**Genome is Good but Annotations Are Poor**

1. Align to reference genome (STAR, HISAT2)
2. Assemble transcripts, genome-guided (Stringtie)
3. Aggregate abundances per gene from transcripts (tximport)
4. DEG Analysis (DESeq2, edgeR)

Another option here is to use a tool like
[PASA](https://github.com/PASApipeline/PASApipeline/wik) to update the
existing annotations if they exist. I've run that pipeline. It's very quirky, a
pain to get running, and if you don't need genomic coordinates I'd avoid it. You
could also use Salmon/Kallisto with StringTie's transcripts, without using its
quantification, but this seems to be an unnecessary step.

**Genome and Transcriptome Are Poor**

1. Assemble transcriptome (Trinity)
2. Pseudoalignment-based abundance estimation (Salmon, Kallisto)
3. Aggregate abundances per gene from transcripts (tximport)
4. DEG Analysis (DESeq2, edgeR)

In this case you're going to want to do a thorough *de-novo* transcriptome
assembly using something like
[Trinity](https://github.com/trinityrnaseq/trinityrnaseq/wiki). This
transcriptome can then be used for pseudoalignment-based abundance estimation and
then DEGs can be determined after aggregation of isoform abundances. Trinity can
be quite a resource hog, so you're going to want to
[get more ram](https://downloadmoreram.com/).

### Why Not Cufflinks/Stringtie For Transcript Assembly In Model Organisms?

First of all, don't use Cufflinks. Stringtie is essentially a more modern
Cufflinks that's
[faster and more accurate](https://ccb.jhu.edu/software/stringtie/index.shtml?t=faq#comp).
Secondly, if you're working in a well annotated genome chances are that "novel
transcripts" you find are more likely noise, or not biologically meaningful
(unless you know better for your use-case!).

### Concluding Thoughts

The paper detailing that transcript abundances, when aggregated to gene level,
improve DEG analysis is particularly interesting. This makes me rethink my usual
assumption and I now believe that tools like Salmon or Kallisto should be the go
to tools for DEG analysis when you have a good transcriptome to work with.

However, I still think it's worthwhile to align your reads and generate a .bam
file. There are many types of visualizations and comparisons that you simply
can't do without them. For example, calculating coverage over featutres of
interest. If you must compare expression of genes across multiple samples or from
different experiments then you'll probably want to convert your expression values
to some normalized measurement. In this case you can use FPKM or TPM, though the
consensus seems to be that TPM is the way to go these days.

And, at the end of the day you know that an out-of-date collaborator is probably
going to ask you for FPKM measurements or something anyway.
