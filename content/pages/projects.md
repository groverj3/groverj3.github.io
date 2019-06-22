Title: Projects
Date: 2019-06-19

### Enabling Reproducible Bioinformatics Workflows
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

If you or your lab are already comfortable working with bioinformatics tools on
a command-line you still face challenges. While the simple solution of writing a
BASH script for each step of a workflow does work, as you run more types of
analyses this gets old very quickly. Your directory structure becomes a mess,
your sysadmin (if you have one) doesn't like you very much, and you fail to make
efficient use of available resources for a workflow (i.e. step 1 needs 8 cores,
step 2 only needs 1, how do I leverage my 28 core system for this?). Even more
concerning, when there are different versions of piecemeal shell scripts floating
around and nobody knows which was used to for sample X.

Enter workflow managers. Snakemake is based on Python and therefore integrates
well with a team accustomed to that language. It intelligently replaces processes
in a workflow to paralellize jobs up to your maximum resources at run-time.

Once a pipeline has been tested and works well, it can be packaged into a
container with Singularity. Similar to Docker, Singularity is optimized for HPC
environments, where normal users can't acquire the permissions to use Docker
containers. This also keeps HPC sysadmins happy because they don't need to
manage your software, plus you can port the analysis to any system you want!

Work is ongoing to implement our lab's pipelines for
[small RNA](https://github.com/boseHere/sRNA_snakemake_workflow) and
[whole-genome bisulfite](https://github.com/groverj3/wgbs_snakemake) sequencing
in such a framework.

### The Role of RNA-directed DNA Methylation in Seed Production

### Genomic Imprinting as a Function of Epigenome State
