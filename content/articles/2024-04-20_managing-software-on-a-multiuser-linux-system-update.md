Title: Managing Software on a Multiuser Linux System - An Update
Date: 2024-04-20
Category: how-to 
tags: sysadmin

Back in 2019, the halcyon days of yore, near the end of my time in graduate school I wrote a well-intentioned article
about software management for multi-user linux systems ([here](/articles/2019-06-25_managing-software-on-a-multiuser-linux-system.html)).
This original article was written based on my experiences as the de-facto sysadmin of our lab's bioinformatics server.
I am not a trained Linux sysadmin, I didn't even major in anything computer-related in college, however, I have been a
big nerd as long as I can remember and have been playing with Linux far longer than I was using it for a job. That
article was a good starting point. However, lots of things have changed in the past few years. While my thoughts are
similar as back then, I do have the benefit of additional experience to draw on, as well as some developments on the
software and hardware side of things since then.

This is not a guide to setting up an HPC or cluster. It's also not a guide for setting up a cloud compute environment.
If you're not at a university or a large company, then you're unlikely to have an HPC. On the flip side, I like cloud
compute, but always like to have a local server for my work. It's just faster to develop on. If you have average compute
needs for bioinformatics (alignment, variant calling, notebooks, etc.) then a single node local server does a very good
job. Especially with modern processors and enough RAM. Plus, if you need more compute you can always get it through your
cloud vendor of choice.

As the only full-time bioinformatics scientist at a midsize biotech company I have once again found myself in the situation
of managing a server for my own work. As we add more people, we need processes that scale well. My goal is to make this
system, augmented with cloud resources, work until reaching 4-5 users.

Consider these tips an addendum to my previous article on the subject.

### 0. Make Your Life Easier With Containers

What is the best way to avoid installing a bunch of random software for your small number of users? Just don't. Encourage
every user to use containers. But how will they do so without `sudo` privileges for Docker? Easy, have them use [Apptainer](https://apptainer.org/)
or [Podman](https://podman.io/). Neither of these options require superuser privileges. Apptainer split off from [Singularity](https://sylabs.io/),
and that is also an option as well. Podman is a Red Hat product, but runs just fine on Ubuntu and other distros, plus it
is *mostly* CLI-identical to Docker. Docker is problematic in HPC and multi-user environments because it requires superuser
permissions, or adding a user to the Docker group (which then allows control of all system containers, also problematic).

A wrinkle to using containers for scientific computing is that usually you don't want the container to continue running
after the job is done. For Apptainer this is fine, it was designed with this use-case in mind. For Podman/Docker, simply
include the `--rm` option in your `docker run` or `podman run`. Another thing to remember is that you're going to have
to mount your directory containing your input data, and output location as a volume for Podman/Docker, or if using
Apptainer and you need to cross filesystem boundaries.

Managing containers is not a big hassle either. You might think that making your own, and putting together a registry is
too much work. Firstly, most bioinformatics and data science software is already available in Docker containers. If not
from the developers, it's likely available through [Biocontainers](https://biocontainers.pro/). In terms of storing them,
you don't need a "real" container registry, you can simply save them like so:

```bash
podman save {container_name} | gzip > container_name.tar.gz
```

If a container is only available for Docker, usually you have convert them to Apptainer/SIngularity format without any
fuss:

```bash
apptainer build {container_name}.sif docker-archive:{container_name}.tar.gz
```

Just stick them somewhere consistent in your directory structure. I use a folder on a NAS called "container_library."

### 1. Encourage Use of Virtual Environments For Python

There is a great extension for pyenv called [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv). When working
on a data science project, or developing a standalone program, one should start by creating a virtualenv for said project.
This is a great solution, in combination with pyenv, for python's terrible package management and dependency resolution.

Yes, you could use Anaconda to do the same thing but Anaconda is bloated and its conda package manager is slow. Plus,
you're then stuck using it for everything. It's pretty easy to install your own local version of python with pyenv, and
then simply run:

```bash
pyenv virtualenv 3.10.2 my-virtual-env-3.10.2
```

The best part of this from a sysadmin perspective is that, again, it's the users' own responsibility to manage all this.
You just give them the tools.

### 2. Users Run Their Own Jupyter Notebook Servers

There are options like [jupyterhub](https://jupyter.org/hub), or [the littlest jupyterhub](https://tljh.jupyter.org/en/latest/).
However, it's even easier to just have users install jupyter in their own python libraries, assign them a port to serve
it on, and have them start it like so:

```bash
jupyter lab --no-browser --port {assigned_port}
```

Then, they can forward that port to your local machine as such:

```bash
ssh -L {assigned_port}:localhost:{assigned_port} {remote_user}@{remote_host_ip}
```

Easy peasy.

### 3. Install R With [rig](https://github.com/r-lib/rig)

One of the more exciting things to happen recently, is the R installation manager, rig. This provides *some* of the same
functionality that you get from pyenv in R. Though, you still can't leave installation of R up to users without having
them run R in a container (a decent option, but makes some things awkward unless you start doing *everything* that way).
Rig lets you install R across the system, without depending on your system package manager. It also configures R to use
the POSIT package manager by default. This is exciting because you no longer need to compile R packages. Yes, there were
ways around this before, but none were very plug and play, and some methods required installing packages for the whole
system. Running `install.package('package_name)` will default to a binary package and then falling back to compilation
if required.

This solution also defaults to user-specific package libraries. So, no need to manage that.

### 4. Have A Real Storage And Backup Strategy

It's not software, but this is a blog and there are no rules. I do what I want. To make sure you never lose critical
data, even if this is just a testing system you need to have a backup strategy. I currently do the following on the
server I manage for that purpose:

1. The / (root) directory is fast NVMe, but not terribly large. Only system files go here.
2. /home is on the same device as /, but users are encouraged to store data elsewhere.
3. / is redundant with a RAID1 configuration storing a mirror of all data to a second identical NVMe drive.
4. /mnt/bulk_nvme is an array of 6 4TB configured as a single volume. Each user gets a directory here symlinked to their
/home. This is where most work happens.
5. /mnt/bulk_nvme is backed up daily to a NAS directly connected to the server via an `rsync` cron job over 10 gigabit ethernet.
6. Commonly used genome/transcriptome references, containers, and other files are available on /mnt/bulk_nvme as well as on the NAS.
7. On the NAS (affectionately named Dagobah, because it's a data "swamp"), there are directories for "data_archive" and
"analysis_results" where raw data and analyzed data live, respectively.
8. The "data_archive," "analysis_results," and "container_library" are backed up to AWS S3 Glacier Instant Retrieval tier.
9. Computational notebooks (jupyter), scripts (BASH, R, Python), and workflow are versioned on github.

This works for now, and is likely to change in order to scale better. In particular, we are looking at automatically
archiving data from a NAS using data lifecycle policies, as well as more complex solutions like [WEKA](https://www.weka.io/).

### 5. Know Where You Draw The Line

Cloud computing is more accessible than ever before. I am personally attached to having *some* local compute for testing,
lighter computation, and direct control. However, if you're not a large organization with existing HPC infrastructure and
don't plan on buying into that, then cloud computing is the way to go. It becomes nearly impossible to predict your cloud
bill, and that's a downside to this. However, if you have more than 2-5 people, and even by the time you get to 4 or 5,
you're going to either need a fulltime *real* sysadmin or you're going to have to use more cloud resources.

We supplement our on-prem compute with AWS. So, if there is a job that requires more RAM than available, uses more CPUs
than we have in one server, or needs powerful GPUs then to the cloud it goes. There are also specific bioinformatics
cloud platforms, and I have opinions on these, but that's for another post.

### Wrap-up

I'm sure there are tens of people out there like me, who don't mind managing a system like this. Regardless, this may give
you some ideas on how to manage your compute environment. I find having a local server more convenient than doing
everything in "the cloud" (someone else's computer), but I have specific limits on this and once reached, augmenting with
cloud resources is a smart thing to reduce admin overhead.

Now, let's see if I can manage more than one post every 4 years.