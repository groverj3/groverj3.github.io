Title: Setting up a Static Site With Pelican and GitHub Pages
Date: 2019-06-15
Category: how-to

In an effort to aid in my future job searching I decided I needed a
personal/professional website. It needed to look good, contain links to my
relevant social and job-search profiles, host some examples of work from my Ph.D.
, showcase my skillset, and host my CV. GitHub pages seemed like a natural fit,
since I already share most of my work there. GitHub recommends static site
generation with Jekyll, which I've seen to be a fine way to do that, and they
have integrated tools for working with it. However, I mostly write python
day-to-day (and R) and the idea of using a ruby-based framework for this just
seemed silly to me. So, stubborn as I am, I decided to embark on a quest to use a
python-based alternative. Pelican seemed to be the most actively developed, so I
went ahead with that.

The issue I ran into is that many of the guides were unnecessarily complicated, 
or didn't contain information for my particular use-case. So, I've compiled here
the steps I used to generate this site, in the hope that it will help others.

### Note Before Starting

Before starting here, I would like to mention that I will not be recommending
using a virtual environment. Why? This is overkill for a simple static site/blog
and adds unnecessary complication to a process that doesn't need to be hard at
all. These sorts of instructions are useful for more advanced deployments, and if
you need them then you probably don't need a guide as simplified as this anyway.

Personally, I **do** use [pyenv](https://github.com/pyenv/pyenv) to manage python
installations on my home and work computers, and well as our lab server. It makes
my life much easier. But it is not **required** so I won't be going over it here.

I still recommend installing python packages at the user level though. Mostly a
*nix/macOS thing, I'm pretty sure Windows peeps can ignore this. This will be
explained where relevant.

This guide will be GNU/Linux centric and I'm not apologizing for it :)

Don't use Python 2.x, it's 2019. I'm writing these with Ubuntu and derivatives in
mind, so I will specify python3 throughout, since I believe `python` still points
to 2.7.

### Step-by-step Instructions Start Here:

Like I said above, there are existing guides for this. However, most of them
recommend installing what amounts to extreme overkill for simple GitHub pages.

1. Have Python and PIP Installed

    If you're on Linux then congrats, you've already got it. If not, consult the
    docs at [python.org](https://www.python.org/)
    
    However, you may not have pip, the python package manager. For that check by
    running:
    
    ```
    which pip3
    ```

    If it doesn't point to an executable then you'll need to run (Ubuntu-based):
    
    ```
    sudo apt install python3-pip
    ```
    
    For other distros/package managers or macOS with homebrew consult the docs to
    get the specific commands. These will likely require superuser/administrator
    privileges.

2. Install Pelican

    On any *nix or macOS machine the following should do the trick in  or
    other terminal:

    ```
    pip3 install --user pelican ghp-import Markdown typogrify
    ```
    
    The `--user` flag installs Pelican to your home directory and doesn't require
    super-user/administrator privileges and `ghp-import` will allow you to push
    directly to github.
    
3. Create a New GitHub Repo and Clone

    It's perfectly fine to use the web interface to create a new repo, so go to
    your github homepage and create a new repository with the name:
    
    `{username}.github.io`
    
    This is important, and will allow you to access your site at
    {username}.github.io rather than needing extra bits on the end of your github
    url. Initializing with a README and LICENSE is up to you! May I recommend the
    MIT license for simplifcity and FOSSness?
    
    Go to your desired dev folder on your machine, I keep all github projects in
    "~/Github/{project_name}", and clone:
    
    ```
    cd {project_folder} && git clone {repo.git}
    ```
    
4. Run Pelican Quickstart in Your Repo Directory

    Pelican comes with a handy quickstart script. Though, it's not terribly-well
    documented. My settings were as follows. Only non-defaults listed (for 
    defaults just push enter):
    
    ```
    pelican quick-start
    ```
    
    > Do you want to specify a URL prefix? Y (Followed by: 
    {https://{username}.github.io})<br> 
    > What is your time zone? {insert local timezone here}<br>
    > Do you want to upload your website using GitHub Pages? Y
    
    This will create the skeleton of your page, and allow you start adding
    content! Other things can be changed later in your config files.
    
5. Create a First Post

    By default, things created in your root level directory are turned into blog
    posts. Don't ask me why this is the default, I don't like it. However, this
    can be changed/hacked around later. For now create a file called `test.md`.
    Add the following to it:
    
    > Title: This is a Blog Post!<br>
    > Date: 2019-06-15<br>
    > Category: Article

    > Hello World!
    
6. Generate Your Site

    There are several ways to do this, this is the simplest:
    
    ```
    make devserver
    ```
    
    This command starts a dev server, which automatically updates the generated
    content in real-time. So you can edit and preview simultaneously. Point your
    web browser of choice to `localhost:8000` and take a look!
    
7. Add a Static Page

    By default, things in the root directory are blog posts (configurable), but
    you'll probably want some static pages that are always linked to and don't
    contain blog content. For that, without stopping the devserver, create a
    new folder inside the "content" subdirectory called "pages":
    
    ```
    mkdir ./content/pages
    ```
    
    Create a new markdown document in there called "about.md":
    
    ```
    touch ./content/pages/about.md
    ```
    
    Fill this with the following:
    
    > Title: About<br>
    > Date: 2019-06-14

    > Hello world! This is a test, using Pelican to create a github pages site.
    
8. Preview Your New Pages

    Go back to your browser, which should have been running the whole time, and
    refresh on `localhost:8000`. You should now see options to go to a new page
    called "about." That's it! Easy peasy!
    
9. Generate Your Content and Push

    Kill the devserver with ctrl + c. Run the following in your root directory:
    
    ```
    make html
    ```
    
    This is probably unnecessary, but in case the devserver wasn't working
    correctly, then this ensures you will have no issues.
    
    Next, run the following to push to github:
    
    ```
    make github
    ```
    
    This will ask for your github username and password, then pushes to your
    repo.
    
    Now direct your browser to:
    
    ```
    https://{username}.github.io
    ```
    
    You site should be visible now!
    
10. Push Your Source Code to a New Branch

    This method of pushing creates a problem from a dev standpoint. It will write
    over all content in your repo every time. Plus, it only writes the rendered
    site there. If you want to work on things off this same machine, you're going
    to want to push the source code. Fortunately, there's an easy workaround for
    this.
    
    Go to the GitHub web interface and create a new branch called "source". This
    will copy all current content to it, which is just the rendered page. Now,
    back in your development folder, copy all content from your repo's folder
    elsewhere (non-hidden stuff only). Then, open a terminal and type:
    
    ```
    git checkout source
    ```
    
    This switches you to the source branch. It also replaces the contents with
    the rendered content-only.
    
    Delete the contents again and replace with your copy of the source code.
    Now enter:
    
    ```
    git add . && git commit -m "Pushed source" && git push -f origin source
    ```
    
    This will force a push to the source branch. Technically you don't need the
    "origin source" since you've checked it out, but for extra safety since we're
    already doing something that is frowned on. This will totally overwrite your
    site's content with the source code used to generate it. But only on that
    branch. Now you can push using the `make github` command, which defaults to
    the master branch, when you want to publish, and push with `git push origin
    source` when you want to update the source code.
    
### Final Thoughts

You're now done! And you can switch between branches to see the source and output
from Pelican's rendering. I'll make another post later to detail some more
configuration details. Until then, the [docs](https://docs.getpelican.com) are a
wonderful resource.
