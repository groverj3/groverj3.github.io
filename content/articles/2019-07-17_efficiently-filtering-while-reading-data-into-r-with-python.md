Title: Efficiently Filtering While Reading Data Into R (With Python?!)
Date: 2019-07-17
Category: how-to 
tags: bioinformatics, data-science, r, python, big-data

Working with large amounts of tabular data is a daily occurance for both
bioinformaticians and data scientists. There's a lot the two groups can learn
from each other (great future post material). However, I recently ran into a
situation that I was sure had to be relatively common. Apparently it wasn't and I
had very little luck checking for a solution in my usual genomics/bioinformatics
cirlces, as well as the data science material I had on-hand.

### The Problem

I recently received output from a large BLAST search. Something on the order of
200,000 queries. Some of those queries had many thousand hits. This is because
the search was completed with minimal filtering. The idea being, it's easy to
post-filter it, but you can't get the hits back that are thrown away. Fair
enough. It was also split between 100+ files. The files were also output in
BLAST's "format 7" (run with --outfmt 7). This means it's tabular (.tsv) with
comment lines throughout. This collection of files was actually too big to load
them into R (where I do most exploratory data analysis) and then filter them. So,
I figured there had to be a way to combine loading and filtering in a
satisfactory way. Of course, you could also pre-filter it with awk or Python
line-by-line and write it out to the hard drive, but this problem interested me.

### **TLDR**

If you have to load **AND** filter you should use the lesser-known
[readr](http://readr.tidyverse.org) function `read_delim_chunked()` (and its
derivatives, `read_{tsv|csv|table}_chunked()`) or write a parser in Python and
translate the resulting object (list of lists, dictionary of lists, or Pandas
dataframe) to R with 
[reticulate](https://rstudio.github.io/reticulate/index.html). The reason behind
this is that iterating through a file and filtering line-by-line, while a
seemingly common thing to do, is horrifically slow in R as far as I can tell. I'm
happy to eat my words if other useRs can prove I'm wrong.

### Attempt #1: Writing a Line-by-line Parser in R

I read all the warnings. They say that R is slow. But is this really true? I
frequently read pretty large files into R with [readr](https://readr.tidyverse.org/)
or [data.table](https://github.com/Rdatatable/data.table/wiki), and they're
*wicked fast*. What I failed to immediately realize is that these packages are
fast because they're written in C/C++ and are effectively compiled programs that
interact with R through its API.

I decided I would test this on both a subset of the data, one of the smaller
files (~2.6 GB), and the first 10,000 lines. The tsv files have comment lines
denoted with '#' and 12 columns which vary between character, float, and
integers:

```R
# Example data
input_file <- 'test_blast_fmt7.out'
system('head -n 10000 test_blast_fmt7.out > test_blast_fmt7.head10000.out')
input_file_head <- 'test_blast_fmt7.head10000.out'
col_names <- c('query', 'subject', 'identity', 'align_length',
               'mismatches', 'gap_opens', 'q_start', 'q_end',
               's_start', 's_end', 'evalue', 'bit_score')
```

I first attempted to solve this problem by writing the following function (don't
do this).

```R
read_filter_blast7_lbl_base <- function (input_file, header, min_perc_id, min_al_len, max_evalue) {
  # Initialize a line counter
  i = 1

  # Open a file connection, yield one line at a time
  out_list <- list()
  conn <- file(input_file, open = 'r')
  while (length(n_line <- readLines(conn, n = 1, warn = FALSE)) > 0) {

    # Split the line at the separator to yield a list, turn into a vector
    line <- unlist(strsplit(n_line, '\t'))

    # Skip comment lines
    if (!startsWith(line[1], '#')) {
      # Include filtering conditions here in this if statement
      if (line[3] >= min_perc_id & line[4] >= min_al_len & line[11] <= max_evalue) {
        out_list[[i]] <- line
      }
    }
    # Count lines
    i = i + 1
  }
  close(conn)

  # Bind the lines as a data frame, don't convert strings to factors
  out_df <- as.data.frame(do.call(rbind, out_list), stringsAsFactors=FALSE)
  colnames(out_df) <- header

  # Set the column classes
  for (i in header[3:12]) {
    out_df[, i] <- as.numeric(out_df[, i])
  }

  # The out_df object will include filtered data, all columns as character vectors
  return(out_df)
}
```

Wow! What an abomination. I'm not sure if this says more about R's unsuitability
to this kind of task or my obvious "Python-think" that's seeping in here. It's a
mess. And it's slow. I tried testing on the first 10,000 lines of one of the
files:

```R
library(microbenchmark)

# Benchmark 100 iterations (default) over the first 10000 lines
> microbenchmark(read_filter_blast7_lbl_base(input_file_head, 80, 432, 1e-50), times = 100)
Unit: milliseconds
                                                                         expr
 read_filter_blast7_lbl_base(input_file_head, col_names, 80, 432,      1e-50)
      min       lq     mean   median       uq    max neval
 338.4403 346.2422 351.0633 349.2319 352.5961 404.62   100
```

It works, but this doesn't scale up to a full file (it sat for ages until I
killed it), and it suffers from R's problems with growing lists in a loop leading
to copying rather than appending. There are clearly other issues too because my
attempts to pre-allocate a list or data frame of the correct size did not speed
it up. This means that I might be doing something wrong. Regardless, this is too
much work to do something so simple. I welcome others to find a pure base R
implementation that's better. It seems like there *should* be a way to do it.

However, there are better options.

### Attempt #2: Using [**sqldf**](https://www.rdocumentation.org/packages/sqldf/versions/0.4-11) to Filter a Temporary sqlite Database

The internet led me to believe that this isn't really something people do in R.
And if you can't load it all into memory then you should use a database and query
that. It seems excessive, but the [sqldf](https://github.com/ggrothendieck/sqldf)
R package can do this. It even includes a function to create the DB on the fly
while reading (`read.csv.sql()`) I totally understand using SQL or similar to query
a DB when you have a reason to query it often and it's stored as an SQL DB. I
question the wisdom of this suggestion though for this purpose. I was able to use
it as follows:

```R
read_filter_blast7_sqldf <- function(input_file, header, min_perc_id, min_al_len, max_evalue) {
  temp_df <- read.csv.sql(
    file = input_file,
    filter = "sed -e '/^#/d'",
    sql = paste0('SELECT * FROM file WHERE V3 >= ', min_perc_id,
                 ' AND V4 >= ', min_al_len, ' AND V11 <= ', max_evalue),
    header = FALSE,
    sep = '\t',
    colClasses = c(rep('character', 2), 'numeric', rep('integer', 7), rep('numeric', 2)),
  )
  colnames(temp_df) <- header
  return(temp_df)
}
```

One of the key limitations here is that you need to pipe through a shell command
(sed) to remove comment lines. Not the biggest deal, but having to write a sed
command does take you out of your flow in an R or jupyter notebook. Let's see
how that performs:

```R
# Benchmark 100 iterations (default) over the first 10000 lines
> microbenchmark(read_filter_blast7_sqldf(input_file_head, col_names, 80, 432, 1e-50), times = 100)
Unit: milliseconds
                                                                      expr
 read_filter_blast7_sqldf(input_file_head, col_names, 80, 432,      1e-50)
      min       lq     mean   median       uq      max neval
 72.27077 73.30782 93.27967 79.38143 103.4807 199.8507   100
```

What's going on here? The max is much slower than the min. This is because the
first iteration reads this into a temporary **file**! This will take
even more time for a larger file, and that temporary database will be the size of
the full, unfiltered file. Usually you load each file once, and each file needs
its own temp sqlite DB. So, the max time is actually the only timing that
matters! Plus, it has the problem of filling up your /tmp directory. What happens
when I try to load the smallest whole file (2.6 GB)?

```R
# Benchmark the whole file once
> microbenchmark(read_filter_blast7_sqldf(input_file, col_names, 80, 432, 1e-50), times = 1)
Unit: seconds
                                                            expr      min
 read_filter_blast7_sqldf(input_file, col_names, 80, 432, 1e-50) 165.4224
       lq     mean   median       uq      max neval
 165.4224 165.4224 165.4224 165.4224 165.4224     1
```

That's decent performance, but because it makes temporary files it will fill up
your /tmp directory:

```bash
$ df -h
Filesystem      Size  Used Avail Use% Mounted on
dev             7.8G     0  7.8G   0% /dev
run             7.8G  1.4M  7.8G   1% /run
/dev/nvme0n1p2  423G   34G  368G   9% /
tmpfs           7.8G  170M  7.6G   3% /dev/shm
tmpfs           7.8G     0  7.8G   0% /sys/fs/cgroup
tmpfs           7.8G  6.9G  913M  89% /tmp
/dev/nvme0n1p1  300M  348K  300M   1% /boot/efi
tmpfs           1.6G   32K  1.6G   1% /run/user/1000
```


And running it on a second file fails:

```R
# Benchmark the whole file once
> microbenchmark(read_filter_blast7_sqldf(input_file, col_names, 80, 432, 1e-50), times = 1)
Error in connection_import_file(conn@ptr, name, value, sep, eol, skip) : 
  RS_sqlite_import: database or disk is full
In addition: Warning message:
In .Internal(gc(verbose, reset, full)) :
  closing unused connection 4 (test_blast_fmt7.out)
Error in result_create(conn@ptr, statement) : 
  cannot rollback - no transaction is active
```

I then had to `sudo rm -r /tmp/Rtmp*` because my ssd was full.

On a system with tons of space it could be fine. I'm running this on my laptop
during a flight so that doesn't help. You could also specify where those
databases are made. However, the largest file I needed to work with is 30 GB and
there were several. And this exact problem happened with that on our lab's
server. (Note to self: Ask my PI to upgrade the root drive).

Still not a great solution.

### Attempt #3: [**readr**](https://readr.tidyverse.org/) `read_delim_chunked()`

This function isn't well-documented, but is the fastest option I found. It's not
quite the line-by-line implementation I thought up, but it's similar. Basically,
it will use readr and a function (user-definable) to bind together dataframes
which are read in chunks. Getting the best performance would require optimizing
the chunk size to the largest you can reasonably handle in memory. I stuck with
10,000 because I was comparing to other options.

```R
library(readr)

read_filter_blast7_readr_chunked <- function (input_file, header, min_perc_id, min_al_len, max_evalue) {

  f <- function(x, pos) subset(x, identity >= min_perc_id & align_length >= min_al_len & evalue <= max_evalue)
  out_df <- read_tsv_chunked(input_file, chunk_size = 10000, col_names = header, comment = '#', callback = DataFrameCallback$new(f))
}
```

Benchmarking results in some very very solid performance:

```R
# Benchmark 100 iterations (default) over the first 10000 lines
> microbenchmark(read_filter_blast7_readr_chunked(input_file_head, col_names, 80, 432, 1e-50), times = 100)
Unit: milliseconds
                                                                              expr
 read_filter_blast7_readr_chunked(input_file_head, col_names,      80, 432, 1e-50)
      min       lq     mean   median       uq      max neval
 28.90464 29.10356 30.87358 29.92421 31.28273 92.10364   100
```

That's not too surprising, since it's basically just reading in the whole file at
once and readr is fast. So, how's it work on the full file?

```R
# Benchmark the whole file once
> microbenchmark(read_filter_blast7_sqldf(input_file, col_names, 80, 432, 1e-50), times = 1)
Unit: seconds
                                                                         expr
 read_filter_blast7_readr_chunked(input_file, col_names, 80, 432,      1e-50)
      min       lq     mean   median       uq      max neval
 76.59867 76.59867 76.59867 76.59867 76.59867 76.59867     1
```

Really good performance. You can tune it better as well, the. This is probably your best bet without getting too
weird. But let's get weird ;)

### Attempt #4: Parse With Python Translate to R With [**reticulate**](https://rstudio.github.io/reticulate/index.html)

Let's do this in Python! Sort of...

Writing a function to read and filter something in a for loop is a common thing
for me in python. I usually don't use Python for exploratory analysis though and
am less familiar with Pandas *et al.* than I am with R's ecosystem. However, I
was able to figure out that it will automatically turn a list of lists into a
dataframe, which is pretty neat. A solid win over R's functionality:

```python3
import pandas as pd

def filter_blast7(input_blast_results, header, min_perc_id, min_al_len,
                  max_evalue):
    df_list = []
    with open(input_blast_results, 'r') as input_handle:
        for line in input_handle:
            if not line.startswith('#'):
                entry = line.strip().split()
                perc_id = float(entry[2])
                al_len = int(entry[3])
                evalue = float(entry[10])
                if (perc_id >= min_perc_id and al_len >= min_al_len
                        and evalue <= max_evalue):
                    df_list.append(entry)
    return pd.DataFrame(df_list, columns=header)
```

This function, when tested in python returns a data frame as expected:

```python3
>>> filter_blast7(input_file_head, col_names, 80, 432, 1e-50).head()
   query     subject    identity align_length mismatches  ... q_end s_start s_end  evalue bit_score
0  query_1  scaffold88  100.000          869          0  ...   869  733052  733920    0.0      1605
1  query_1  scaffold88   95.732          867         34  ...   869  734435  735298    0.0      1393
2  query_1   scaffold1  100.000          869          0  ...   869    4053    4921    0.0      1605
3  query_1   scaffold1   95.732          867         34  ...   869    5436    6299    0.0      1393
4  query_3  scaffold88  100.000          786          0  ...   786  735004  735789    0.0      1452
```

Nice, but I thought we were using R? Well, we can actually use the R package
[reticulate](https://rstudio.github.io/reticulate/index.html) to run this python
code and translate its output to an R data frame. Pretty neat! You can get it
from CRAN with `install.packages('reticulate')`. With it installed you'll want to
make sure it can find your python installation:

```R
> library(reticulate)
> py_discover_config()
python:         /home/groverj3/.pyenv/shims/python
libpython:      /home/groverj3/.pyenv/versions/3.7.2/lib/libpython3.7m.so
pythonhome:     /home/groverj3/.pyenv/versions/3.7.2:/home/groverj3/.pyenv/versions/3.7.2
version:        3.7.2 (default, Mar 17 2019, 02:15:50)  [GCC 8.2.1 20181127]
numpy:          /home/groverj3/.local/lib/python3.7/site-packages/numpy
numpy_version:  1.16.4

python versions found: 
 /home/groverj3/.pyenv/shims/python
 /usr/bin/python
 /usr/bin/python3
> py_available()
[1] FALSE
> py_available(initialize = TRUE)
[1] TRUE
```

Even though it found my python installation `py_available()` returns false? I
just forced it to true. I think this is because I use
[pyenv](https://github.com/pyenv/pyenv) to manage my non-system python
installation. This also required making sure the python shared library is
installed (which it is not when installed with pyenv). Now, you can either
source the python parsing function from a saved .py script, or run it inline as
follows, and coerce it to an R function:

```R
read_filter_blast7_lbl_py <- py_run_string(
"import pandas as pd

def filter_blast7(input_blast_results, header, min_perc_id, min_al_len,
                   max_evalue):
    df_list = []
    with open(input_blast_results, 'r') as input_handle:
        for line in input_handle:
            if not line.startswith('#'):
                entry = line.strip().split()
                perc_id = float(entry[2])
                al_len = int(entry[3])
                evalue = float(entry[10])
                if (
                    perc_id >= min_perc_id
                    and al_len >= min_al_len
                    and evalue <= max_evalue
                ):
                    df_list.append(entry)
    return pd.DataFrame(df_list, columns=header)"
)$filter_blast7
```

Which shows up as a "python.builtin.function."

```R
class(read_filter_blast7_lbl_py)
[1] "python.builtin.function" "python.builtin.object"  
```

Now, let's benchmark that:

```R
> # Benchmark 100 iterations over the first 10000 lines
> microbenchmark(read_filter_blast7_lbl_py(input_file_head, col_names, 80, 432, 1e-50), times = 100)
Unit: milliseconds
                                                                       expr
 read_filter_blast7_lbl_py(input_file_head, col_names, 80, 432,      1e-50)
      min       lq     mean   median       uq      max neval
 60.73332 62.57396 67.58808 63.75887 69.98544 105.8659   100
> 
> # Benchmark the whole file once
> microbenchmark(read_filter_blast7_lbl_py(input_file, col_names, 80, 432, 1e-50), times = 1)
Unit: seconds
                                                             expr      min
 read_filter_blast7_lbl_py(input_file, col_names, 80, 432, 1e-50) 139.1212
       lq     mean   median       uq      max neval
 139.1212 139.1212 139.1212 139.1212 139.1212     1
> 
```

It also returns a data frame identical to the python one:

```R
head(read_filter_blast7_lbl_py(input_file_head, col_names, 80, 432, 1e-50))
  query    subject    identity align_length mismatches
1 query_1 scaffold88  100.000          869          0
2 query_1 scaffold88   95.732          867         34
3 query_1  scaffold1  100.000          869          0
4 query_1  scaffold1   95.732          867         34
5 query_3 scaffold88  100.000          786          0
6 query_3  scaffold1  100.000          786          0
  gap_opens q_start q_end s_start  s_end evalue bit_score
1         0       1   869  733052 733920    0.0      1605
2         1       3   869  734435 735298    0.0      1393
3         0       1   869    4053   4921    0.0      1605
4         1       3   869    5436   6299    0.0      1393
5         0       1   786  735004 735789    0.0      1452
6         0       1   786    6005   6790    0.0      1452
```

It's definitely not as fast as reading it chunked with readr. However, that
Python function was easy to write and performed far better than the base R way to
read and filter line-by-line. In the future, if I have something that I know how
to do in Python I may not try to translate it to R. Just run the python code with
reticulate! 

### Wrapping Things Up

You would think that is a commonly done thing, to filter huge datasets while
reading. Apparently, it's not common enough in R for good documentation to exist.
In the end readr wins again with `read_delim_chunked()`. This does require some
tuning to get the best performance, but if you pick some sane chunk_size then
further opitmization is probably unnecessary and it will work fine. However, the
revelation that communicating between python and R works so well opens up a lot
of future possibilities! Some things are just better suited to one language or
another. While Python has pandas dataframes and a large ecosystem around them
none of it is as intuitive as the [tidyverse](https://www.tidyverse.org/) (to
me). Something like the two winners here are ideal for situations where you have
a huge file to load, but you know that most of the file will not meet your
filtering criteria.

Using Python to do general purpose programming and communicating those results to
R for statistical testing and visualization is definitely something to consider.

### Addendum: What's the Overhead of Filtering While reading?

Let's check it out, first the readr method:

```R
> microbenchmark(read_tsv(input_file, col_names=col_names, comment='#'), times = 1)
Parsed with column specification:
cols(
  query = col_character(),
  subject = col_character(),
  identity = col_double(),
  align_length = col_double(),
  mismatches = col_double(),
  gap_opens = col_double(),
  q_start = col_double(),
  q_end = col_double(),
  s_start = col_double(),
  s_end = col_double(),
  evalue = col_double(),
  bit_score = col_double()
)
|=================================================================| 100% 2685 MB
Unit: seconds
                                                       expr      min       lq
 read_tsv(input_file, col_names = col_names, comment = "#") 64.35369 64.35369
     mean   median       uq      max neval
 64.35369 64.35369 64.35369 64.35369     1
```

This is compared with 76.59867 ms for filtering. That's basically no difference.
How about the reading it in with Python using Pandas read_csv:

```R
> read_csv_py <- py_run_string(
"def read_blast7(input_blast_results, header):
    return pd.read_csv(input_blast_results, sep='\t', comment='#')"
)$read_blast7

> # Benchmark the whole file once
> microbenchmark(read_csv_py(input_file, col_names), times = 1)
Unit: seconds
                               expr      min       lq     mean   median
 read_csv_py(input_file, col_names) 97.45004 97.45004 97.45004 97.45004
       uq      max neval
 97.45004 97.45004     1
```

There's clearly a bit of overhead with both of these methods, but it's pretty
minor, on the order of 10-30 ms for a 2.6 gb file.
