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

#### **Spatiotemporal Dynamics of sRNA Expression and DNA Methylation in Seed Development**

Our finding that seed development in *B. rapa* depends on the RdDM machinery
opens up many new avenues of discovery. Currently, we are focused on how the
sRNA-ome and methylome changes throughout seed development and compared to
sporophytic tissues. This work is ongoing.

## Genomic Imprinting as a Function of Epigenome State

#### **Does RdDM Control Genomic Imprinting at Developmentally Important Genes?**

Genomic imprinting, or biased expression of parental alleles is a phenomenon seen
in both plants and animals. In plants known examples occur in the endosperm, a
nutritive tissue within the seed that provides energy for the growing embryo. In
this case biased expression would mean a deviation from the expected 3:1 ratio of
maternal to paternal gene expression, as the endosperm is a triploid tissue and
created by the fusion of a single sperm with the diploid central cell during
double fertilization.

Previous work has implicated small RNAs and DNA methylation in genomic impriting
and we are investigating it in *Brassica rapa* with a focus on RdDM. *B . rapa*
is a recently outbreeding species and therefore it is expected that there would
be increased conflict between parental genomes compared with *Arabidopsis 
thaliana*, where most work on imprinting has been done.
