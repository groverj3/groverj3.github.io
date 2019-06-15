#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Jeffrey Grover'
SITENAME = "Jeff's Little Slice of the Web"
SITEURL = ''
SITELOGO = '/images/jeff.jpg'
SITETITLE = AUTHOR
SITESUBTITLE = '''Bioinformatician/Ph.D. Candidate<br>
<a href="https://cals.arizona.edu/research/mosherlab/Mosher_Lab/Home.html" target="_blank">The Mosher Lab</a>
@ <a href="https://www.arizona.edu/" target="_blank">The University of Arizona</a>'''

TIMEZONE = 'America/Phoenix'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Sidebar links
LINKS = (
    ('Home', '/'),
    ('About', '/pages/about.html'),
)

# Social widget
SOCIAL = (
    ('linkedin', 'https://www.linkedin.com/in/jeffreygrover/'),
    ('github', 'https://github.com/groverj3')
)

# Pagination setting
DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

# Don't keep old files
DELETE_OUTPUT_DIRECTORY = True

# Theming
THEME = 'Flex'
MAIN_MENU = False
DISPLAY_PAGES_ON_MENU = False
PATH = 'content'
STATIC_PATHS = ['images']
