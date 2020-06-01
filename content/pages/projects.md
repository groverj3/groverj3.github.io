Title: Projects
Date: 2019-06-19

## Enabling Reproducible Bioinformatics Workflows
#### [**LoadExp+**](https://genomevolution.org/coge/LoadExperiment.pl)

As the prices for sequencing techologies have decreasaed many researchers are now
able to conduct large experiments on the genomic and even metagenomic scales.
This progression is exciting, and the need for computational expertise in the
biological sciences has never been greater! However, the need for this experience
has greatly surpassed the number of trained individuals, and not every lab wants
to invest the time into learning these new technologies. They want to answer
scientific questions!

I worked with Dr. Eric Lyons' lab at The University of Arizona to add analysis
workflows to their web-based comparative genomics resource,
[CoGe](https://genomevolution.org). These workflows, collectively called
["LoadExp+"](https://genomevolution.org/wiki/index.php/LoadExp%2B) allow
researchers upload raw data from their local machine or from cloud storage by
integration with the [CyVerse](http://www.cyverse.org) Datastore. Output files
are automatically organized into digital "notebooks" to be shared with
colaborators or kept private if desired. Each experiment's files are also
viewable as tracks in CoGe's integrated genome browser
([Epic-Coge](https://genomevolution.org/wiki/index.php/EPIC-CoGe)). This enables
researchers to run LoadExp+ workflows using any available genome in CoGe,
including those uploaded by users themselves.

[**Read The Publication!**](https://doi.org/10.1002/pld3.8)

#### **Automated Analysis Pipelines With [Snakemake](https://snakemake.readthedocs.io/en/stable/) and [Singularity](https://sylabs.io/)**

While the simple solution of writing a BASH script for each step of a workflow
does work, as you run more types of analyses this doesn't scale well. Your
directory structure becomes a mess and you fail to make efficient use of
available resources for a workflow (i.e. step 1 needs 8 cores, step 2 only needs
1, how do I leverage my 28 core system for this?). Even more concerning, when
there are different versions of piecemeal shell scripts floating around and
nobody knows which was used to for sample X.

Snakemake is simple and full featured workflow manager based on Python. It
intelligently replaces processes in a workflow to paralellize jobs up to your
maximum resources at run-time. Once a pipeline has been tested it can be packaged
into a container with Singularity. Similar to Docker, Singularity is optimized
for HPC environments. This keeps HPC sysadmins happy because they don't need to
manage your software, plus you can port the analysis to any system you want!

Work is ongoing to implement our lab's pipelines for
[small RNA](https://github.com/boseHere/sRNA_snakemake_workflow) and
[whole-genome bisulfite](https://github.com/groverj3/wgbs_snakemake) sequencing
in such a framework.

## The Role of RNA-directed DNA Methylation in Seed Development

#### **[Maternal components of RNA‐directed DNA methylation are required for seed development in <i>Brassica rapa</i>](https://onlinelibrary.wiley.com/doi/full/10.1111/tpj.13910)**

It's been widely observed that RdDM and 24 nucleotide small RNAs are correlated
with reproductive processes. This is due to specific methylation patterns in
reproductive tissues and the high abundance of small RNAs in seeds and flowers.
Most of this work has been done in *Arabidopsis thaliana* a premier model
organism in plant biology. However, *A. thaliana's* small, TE-poor, genome is not
typical of most plants and therefore we are investigating the connection between
plant reproduction and RdDM in *Brassica rapa* a closely related, recently
outbreeding species which shows severe defects in seed development in RdDM
mutants.

We have identified mutations in several RdDM pathway genes, annotated RNA Pol
IV/RDR2-dependent small RNA loci, and determined which genes are differentially
expressed in RdDM mutant ovules and seeds. We have also found that it is the
maternal sporophytic genome that determines whether the seed developmental
defect will be present.

[**You can check out the publication here!**](https://onlinelibrary.wiley.com/doi/full/10.1111/tpj.13910).

#### **[Abundant expression of maternal siRNAs is a conserved feature of seed development](https://doi.org/10.1101/866806)**

Our finding that seed development in *B. rapa* depends on the RdDM machinery
opens up many new avenues of discovery. We expanded upon this research by
investigating the dynamics of small RNA expression and accumulation genome-wide
in seeds. From this large collection of sequencing data we identified a subset of
small RNA loci that account for the vast majority of small RNA expression in
seeds. These loci were identified as siren loci, after a similar category that
had been observed in rice endosperm.

Siren loci are unique amongst small RNA loci. They accumulate Pol IV-dependent
small RNAs and direct DNA methylation, but in a tissue-specific manner.
Additionally, siren RNAs tend to be expressed only from maternal chromosomes even
when functional paternal RdDM machinery is present in the endosperm. Finally,
siren loci and siren RNAs are dependent only on maternal RdDM machinery in the
seed and are present in multiple species. This indicates that siren loci may be
a general feature of seeds, and may be required for seed production in some
species.

[**You can check out the publication here!**](https://doi.org/10.1101/866806).
