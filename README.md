# Introduction

For a while I've been running the excellent [dokuwiki](https://www.dokuwiki.org) on my Mac using OS X's bundled Apache server. The problem is that every time Apple update the OS they futz with the Apache config, so I have to work out how to get it going again. Then I have to update `dokuwiki` itself, as I don't do that nearly as often as I should. Etc, etc. However, it struck me that I don't really need a wiki as such---all I really need are inter-page links and the ability to tag pages and gets lists of pages that match a given set of tags. (This is basically DokuWiki's double bracket syntax: `[[A Page Title]] ` and the [tag](https://www.dokuwiki.org/plugin:tag) plugin.) I don't actually need the "wiki" bit, as I can easily edit the files locally and deploy as needed. I've also got used to using Markdown rather than DokuWiki's markup (although there is a Markdown plugin for that).

So this project hosts a Python script (`moku-wiki`) that takes an input folder of Markdown documents and processes them according to the following rules, putting the results in an output folder:

*  Inter-page links can be specified using the target page's title, e.g. `[[A Page Title]]`. This is converted to a standard Markdown link to the HTML version of that page: `[A Page Title](a_page_title.html)`.
*  Tags can be specified in the YAML. Tags can be referenced in a page using the following syntax: `{{tag1}}`. This will produce a list of page links that have the "tag1" tag.

As an example, here is a typical input file:

```
---
title: The First Page
author: Phil
tags: [abc, def]
...

This is the first page. There may be more. Here is a link to [[Another Page]].

## List of pages in ABC

{{abc}}

### List of all pages in mock wiki

{{*}}

```

This will produce:

```
---
title: The First Page
author: Phil
tags: [abc, def]
...

This is the first page. There may be more. Here is a link to [Another Page](another_page.html).

## List of pages in ABC

[The First Page](the_first_page.html)

[An ABC Page](an_abc_page.html)

### List of all pages in mock wiki

[The First Page](the_first_page.html)

[An ABC Page](an_abc_page.html)

[A DEF Page](a_def_page.html)

```

Note that only the page and tag links are converted, everything else should be left the same. Also note that:

1.  The YAML metadata format must be used (and the end of the block must indicated with `...` not `---`).
2.  If a page does not have a "title" key in the metadata then processing is skipped.
3.  The "title" cannot contain parentheses or brackets (basically just alpha-numeric characters and some punctuation).
4.  The output filename of a file will be a "slugified" version of the title (which might completely unrelated to the *input* filename). So an input file with the name "file1.md" and a title of "A Page Title" will produce an output file named "a_page_title.md" in the output folder.
5.  You can define a "display" name using `[[Display Name|A Page Name]]` which will become `[Display Name](a_page_name.html)`.
6.  It assumes that the eventual output will be HTML, so the links end in ".html".
7.  If an equivalent title cannot be found for a link then it outputs a bracketed span with the class "broken", e.g. `[No Such Page]{.broken}`. This can be used to style broken links.
8.  Tags must be in a YAML list (i.e. enclosed in brackets).
9.  Tags cannot contain spaces, brackets or punctuation (specify multi-word tags with underscores "like_this").
10.  Additional tags can be specified using various operators:
    a. "tag1 tag2" includes pages with tag1 *or* tag2
    b. "tag1 +tag2" includes pages with tag1 *and* tag2
    c. "tag1 -tag2" includes pages with tag1 that do *not* have tag2
    d. "*" is a shortcut to include _all_ pages in the wiki that have a tag (pages do not have to have a tag, so leave them out if you don't want them in this "index" list)

The script does **NOT** convert the Markdown to HTML (or anything else). It simply converts the page/tag links in preparation for such conversion. As such it could be used in conjunction with the various static web site generators out there.

> NOTE: Originally the project was referred to as "fake wiki". This brought to mind "mock wiki", and in a fit of alliterative humour I changed it to "moku-wiki" in homage to *DokuWiki*. This should not be construed as "mocking" *DokuWiki*---far from it! *DokuWiki* is a great piece of software.

# Installation

Copy the `moku-wiki` file to somewhere in your path (e.g. `/usr/local/bin` on a Unix based system). The supplied `ant` build.xml does this with `$ ant deploy`.

# Usage

```
$ moku-wiki input-dir output-dir
```

# Assumptions

1.  [pandoc](pandoc.org) is being used as the Markdown processor (or at least, some converter that supports the `pandoc` Markdown syntax). The processor will need YAML metadata support.

# Caveats

1.  This is my first Python project (yay!), so it's been cobbled together from Stack Overflow answers. As a result it's probably not the best Python code out there but it does at least work... more or less.
2.  Error checking/handling is minimal/woefully inadequate.
3.  There are lots of things you can't do (spaces in tag names, brackets in titles etc) that could probably be addressed by better regular expressions or a more complete model of what's going on.
4.  `moku-wiki` only converts the page link and tag list markup---anything else will have to be done by say, a `pandoc` template or similar.
5.  There is no conflict checking, so if two pages have the same title then there will be problems. 

# To Do

1.  Better error handling.
2.  Search. In this case the internal index would be dumped to a JSON file which would allow a simple Javascript function to search for a keyword and display the pages that matched. It's not great but would retain the 'static' nature of sites generated by `moku-wiki`. Could maybe include `keywords` in the file's YAML metadata to add to the index (or even just index every word in the file, but that might be too big).
3.  Better indexing. Currently each file is read once to create the index, then they are all read again so that the tag links can be resolved. There may be a more efficient way to do this using a database, or some other new-fangled doohickey, but in tests the time taken for the script to run is negligable compared to the "conversion to HTML" step.

