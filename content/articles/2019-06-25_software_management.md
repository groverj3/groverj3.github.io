Title: Managing Software on a Multiuser Linux System
Date: 2019-06-25
Category: how-to 
tags: sysadmin

When I started my Ph.D. I had a good amount of experience working in a Linux
environment on my own computers. Mostly as a hobby. My advisor had bought a small
server several years previous for a post-doc's project and I was offered this
system to use for my day-to-day work. It doesn't set any speed records, but it
*is* a 24 thread system with 75gb of RAM and 12TB of storage. This makes it
perfect for running analyses that I wouldn't want to do on my laptop, but need to
be tweaked repeatedly and therefore are awkward to run on the university HPC. I
also use this server for jupyter notebooks and it still handles a few users at
a time well.

Since this system was starting from a blank slate I decided to implement some
simple rules for system management. When I started out I was the only user, but
since then we've added several others and this plan has held up. This is going to
be heavily biased toward running a small server for computational work that's
shared between < 10 users, because that's what I do.

These are ordered, but feel free to ignore that. They're really more like general
tips.

### 0. Run a Well-Supported (Popular) Linux Server Distro

I know, I know, I know. You may have a favorite Linux distribution. It might be
[Fedora](https://getfedora.org/), or [Mint](https://linuxmint.com/), or
[Manjaro](https://manjaro.org/) (that's what I've been using). You might use
[Arch](https://www.archlinux.org/), you might be a [masochist](https://www.gentoo.org/),
or you may enjoy running something with an innovative package management system
like [Guix](https://www.gnu.org/software/guix/) or [NixOS](https://nixos.org/).

Maybe you just don't know why everyone uses this \*nix stuff and don't know why
you can't just bioinformatics in Excel.

<center>
<img src="/images/clippy_bioinfo.png">
</center>

You're welcome to use something flashier, but I'd recommend sticking to Ubuntu
Server or CentOS. Fedora Server might also be a good choice. Especially with
Ubuntu potentially not shipping 32bit support in the future. For those with more
time or inclination to fiddle around, Debian would also make a good research
computing environment. The reason for this is that most software that's already
packaged will be either in .deb (Debian and derivate, including Ubuntu) or .rpm
(Redhat, Fedora, SUSE) format. Can you extract these packages and install them on
other systems? Sure. Are you going to want to do that every time you update
stuff. No.

You also want to make sure that required libraries for software you may need to
compile are available without much fussing around straight from the repositories.
You'll have to do enough annoying things. Don't make this annoying.

### 1. Revoke Other Users' **sudo** Privileges

This may seem obvious but you'd be surprised how many academic labs don't think
about this on their private server (if they have one). It's hard to overstate the
terrible time you'll have as a sysadmin if another one of your users types the
dreaded:

```bash
sudo rm -r /
```

or

```bash
sudo rm -r /*
```

It's easy to forget that "." before the "/". 

Or, less catasrophically, that user may try installing software in a brittle way.
Meaning, you, the humble pseudo-sysadmin who's not actually getting paid for
sysadmin tasks, will have to spend time fixing it.

All it takes is for you, the SUPER USER, the GOD OF THE SERVER, to run:

```bash
sudo deluser {USERNAME} sudo
```

Replace {USERNAME} with the user to remove.

### 2. Don't Blindly Install Software From Your Distro's Repos

I did just say to pick a distro with lots of stuff in the repos, right? Yes, but
particularly in scientific/research computing you really really really can't
assume these repos are anything close to up-to-date. Don't be afraid to download
the source code and compile, or even easier, there is likely a prebuilt
binary release available on the project's github.

As an example, if you're running the most recent LTS version of Ubuntu (18.04)
then the version of samtools available to you is v1.7 which is a year and a half
old at the time of writing. If you have control of the system, then at least try
to install the most recent stable versions of critical software.

### 3. Use an Easily Followed Convention for Manual Software Installation

When you need to download software and install it manually put it somewhere easy
to remember, and easy to find for others. I put manually installed software in
/opt/software_version and symlink the binaries to /usr/local/bin/. This way,
you quickly know what you have manually installed, and what version they are just
from the directory structure. You also make everything available in the $PATH and
runnable with just the program name.

The worst thing that can happen in a broken symlink if you change software
versions, and that's an easy fix with a:

```bash
sudo ln -s /path/to/binary /usr/local/bin
```

### 4. Encourage Users To Test Software in ~/bin

Create a private bin directory inside each user's home folder. This is often
pre-configured in each user's path. If not you'll need to add it to each user's
.bashrc or .profile or .bash_profile, depending on which is the preferred method
for your distro:

```bash
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi
```

Let your users test and if multiple people need it, or they're running something
all the time then you can install it system-wide in /opt.

### 5. Encourage Python Users to Set Up [pyenv](https://github.com/pyenv/pyenv)

Linux systems use Python under the hood a lot. Much of the system depends on
python, and your distro's package manager has already likely installed many
python packages. However, these versions are likely old and frozen at the version
number that shipped with the OS. I dislike running software that is *years* out
of date. Python's package management with pip is kind of a mess and it doesn't
know which packages are needed by the system, and which are installed with it.
This is improving over time, but it's still not good.

To avoid this, users should install the most recent stable version of Python.
Pyenv gives you a relatively easy and very lightweight way to do this. It also
allows the system packages to coexist peacefully in the root directory so it's
harder to break things. Plus, the users get the latest Python features.

The [pyenv github](https://github.com/pyenv/pyenv) has relatively easy to follow
instructions.

### 6. Use User-specific Lnaguage Libraries/Packages

This pops up for us with both python and R. It boils down to never, ever, using:

```bash
sudo pip install {PACKAGE_NAME}
```

or

```R
sudo R
install.packages('PACKAGE_NAME')
```

If users can't use sudo there's no danger here anyway, but using user-specific
libraries and packages keeps things consistent. It also means that, once again,
you don't have to manage something. The following will solve this for Python:

```bash
pip install --user {PACKAGE_NAME}
```

This installs packages to ~/.local/lib/python{VERSION}/site-packages 

R requires a bit more doing. To create a user-library I recommend creating a
.Renviron in each user's home directory and adding the following to it.

```R
# .Renviron is run every time a new R session is started
# Use .Renviron to set environment variables for R

# Use the local R library
R_LIBS_USER="~/.local/lib/R/site-library"
```

### Wrapping up

In summary, administering a small multi-user system doesn't have to be
complicated. You do want to minimize the ability for your users to break things
though. By no means is this an exhaustive guide, but it might help you out if
you're wondering where to start.

Despite the proliferation of HPC systems at Universities, and cloud computing in
enterprise environments, a smaller server for your research group is still a
good investment in 2019. Submitting jobs to a queue is fine when you're not doing
iterative work, but if you want to quickly test things it gets old really quick.
Likewise, you can easily get hardware on-par with a remote VM and it's more
readily accessed.

Tune in next time for something more bioinformatics-focused!
