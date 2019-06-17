#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Overall site settings
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
PATH = 'content'
ARTICLE_PATHS = ['articles']
PAGE_PATHS = ['pages']
STATIC_PATHS = ['images']
INDEX_SAVE_AS = '/pages/blog.html'

# Theming
THEME = 'Flex'
MAIN_MENU = True

# Feed generation - unused currently
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Sidebar links - using LINKS instead of default sidebar for PAGES
# Theme was forked and edited to prevent opening LINKS in new windows
DISPLAY_PAGES_ON_MENU = False
LINKS = (
    ('About', '/pages/about.html'),
    ('Blog', '/pages/blog.html'),
)

# Social widget
SOCIAL = (
    ('envelope', 'mailto:groverj3@gmail.com'),
    ('linkedin', 'https://www.linkedin.com/in/jeffreygrover/'),
    ('github', 'https://github.com/groverj3'),
)

# Main menu - actually the menu at the top and bottom of pages
MENUITEMS = (
    ('About', '/pages/about.html'),
    ('Blog', '/pages/blog.html'),
    ('Categories', '/categories.html'),
)

# Pagination setting
DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

# Don't keep old files
DELETE_OUTPUT_DIRECTORY = True
