# Introduction

For a while I've been running the excellent [DokuWiki](https://www.dokuwiki.org) on my Mac using OS X's bundled Apache server. The problem is that every time Apple update the OS they futz with the Apache config, so I have to work out how to get it going again. Then I have to update `DokuWiki` itself, as I don't do that nearly as often as I should. Etc, etc.

However, it struck me that I don't really need a wiki as such---all I really need for my purposes are inter-page links (within pages in the same folder, usually) and the ability to tag pages and then get lists of pages that match a given set of tags. (This is basically DokuWiki's double bracket syntax for links to another page: `[[A Page Title]] ` and the [tag](https://www.dokuwiki.org/plugin:tag) plugin.) I don't actually need the "wiki" bit, as I can easily edit the files locally and compile/deploy as needed. I've also got used to using Markdown rather than DokuWiki's markup (although there is a Markdown plugin for that but it's not Pandoc Markdown, and so on).

So this project hosts a Python script (`mokuwiki.py`) that takes an input folder of Markdown documents and processes them according to the following rules, putting the results in an output folder:

*  Inter-page links can be specified using the target page's title (as specified in the YAML metadata block), e.g. `[[A Page Title]]`. This is converted to a standard Markdown link to the HTML version of the page with that title: `[A Page Title](a_page_title.html)`.
*   The YAML metadata can also have an "alias" field which can be used to link to that page instead of the title. This can be useful if the actual title that is to be displayed (the "formal" title, if you will) is long but has a common shorter form. Aliases must be unique and not the same as any
title.
*  Tags can be specified in the YAML. Tags can be referenced in a page using the following syntax: `{{tag1}}`. This will produce a list of page links that have the "tag1" tag.
*  Include one file in another using the following markup: `<<include_me.md>>`. Any YAML data blocks will be removed from the included file. This pattern actually supports globbing, so you can do `<<include_X*Y.dat>>` and so on. Blank lines will be inserted between each file, and separators can be inserted between each one by using the syntax `<include_X*Y.dat|* * *>>`. (The default is no separator, but "* * *" is a useful one as it becomes a horizontal rule when processed by `pandoc`. Also the path is assumed to be relative to the directory that the module was invoked from.)
*  You can also insert image links using a shortcut, although this assumes that the images are named after their caption: `!!A Nice Image!!` will be converted to `![A Nice Image](images/a_nice_image.jpg)`. Note that it is assumed that images live in an "images" folder (this can be changed using the "--media" command line option) and that they are JPGs. Change the extension using this syntax: `!!Another Picture|png!!`.

As an example, here is a typical input file:

```
---
title: The First Page
alias: Page 1
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
alias: Page 1
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

Note that only the MokuWiki specific "markup" is converted, everything else should be left the same. Also note that:

1.  The YAML metadata format must be used (and the end of the block must indicated with `...`, not with `---`).
2.  If a page does not have a "title" key in the metadata then processing of that file is skipped.
3.  The "title" cannot contain parentheses or brackets (basically just alpha-numeric characters and some punctuation).
4.  The output filename of a file will be a "slugified" version of the title (which might completely unrelated to the *input* filename). So an input file with the name "file1.md" and a title of "A Page Title" will produce an output file named "a_page_title.md" in the output folder.
    a. You can fool the system by having two documents with the same title but with different case. Don't do that...
5.  You can define a "display" name using the syntax `[[Display Name|A Page Name]]` which will become `[Display Name](a_page_name.html)`. (Note: unlike the DokuWiki syntax you cannot specify an actual filename here.)
6.  It assumes that the eventual output will be HTML, so the links end in ".html".
7.  If an equivalent title cannot be found for a link then it outputs a bracketed span with the class "broken", e.g. `[No Such Page]{.broken}`. This can be used to style broken links. The class name can be changed using the `--broken` command line option.
8.  Tags must be in a YAML list (i.e. enclosed in brackets, separated by commas), e.g. `tags: [foo, bar]`.
9.  Tag names cannot contain brackets or punctuation. When being defined in the YAML block tags can contain spaces, e.g. `tags: [Wordy Tag, Other Tag]`. However, when referencing tags with spaces use an underscore instead of a space, e.g. `{{Wordy_Tag +other_tag}}`. Tag names are case-insensitive.
10. Tags can be combined using various operators:
    a. "{{tag1 tag2}}" includes pages with tag1 *or* tag2
    b. "{{tag1 +tag2}}" includes pages with tag1 *and* tag2
    c. "{{tag1 -tag2}}" includes pages with tag1 that do *not* have tag2
    d. "{{*}}" is a shortcut to include *all* pages in the wiki that have a tag (pages do not have to have a tag, so leave them out if you don't want them in this "index" list)
    e. "{{#}}" is a shortcut for the number of pages that have a tag
    f. "{{#tag1}}" returns the number of pages that have the tag 'tag1'
    g. "{{@}}" will return a list of all tags as a series of bracketed spans with the class name "tag". This can be used to style tag lists. The class name can be changed using the `--tag` command line option.
11. Page names can contain references to namespaces, e.g. `[[ns2:Page Four]]`. Namespaces are assumed to refer to folders and so cannot contain spaces. How these are incorporated into the resulting link depends on whether the `--fullns` command line option is set:
    a. When not set (the default) it assumes that there is a main folder, with a single level of child folders, e.g. "main/a", "main/b" and so on. A namespace reference in a page in the folder "main/a" is assumed to point to a page in a sibling folder. Therefore an inter-page link like `[[b:A Page]]` in a document in "main/a" will convert to `[A Page](../b/a_page.html)`.
    b. When `--fullns` is set it will treat a namespace as a full path of folders. The author is then responsible for specifying the correct path, e.g. `[[..:..:ns2:ns3:A Page]]` will become `[A Page](../../ns2/n3/a_page.html)`.
12. On the command line the source directory can actually be a path specification, e.g. `pages/file*.md` which will process only those files. Be sure to escape any wild cards from the shell, i.e. `pages/file\*.md`.
13. Single file mode can be enabled with the `--single` option. Only a single input file is expected and the output file given on the command line is used 'as-is' for the output (i.e. is assumed to be the intended output file name). This is not very useful for page links and tags but can be very handy for including files in the specified input file. The search index option is disabled in single file mode.

The script does **NOT** convert the Markdown to HTML (or anything else). It simply converts the page/tag links in preparation for such conversion. As such it could be used in conjunction with the various static web site generators out there.

Use the "--list" option to output a list of page links that do not exist.

The optional command line option "--index" will output a JSON file (called "_index.json") which contains an index of titles, file names and terms contained in each page. This can be used to create a simplistic search function in the "wiki". This has the format:

```
var MW = MW || {};
MW.searchIndex = [
    {
      "file" : "file_name",
      "title" : "The Title",
      "terms" : "word1 word2 word3"
    },
    ...
]
```

Some assumptions are made here, namely that this file will be included using a `<script>` statement so to be accessible it needs to be in a variable. In a primitive attempt to encapsulate things I've assumed that there is an "MW" object used to store any MokuWiki related data and the index is stored under its "searchIndex" property.

The string in "terms" is a list of all words that occur in the following metadata elements of the file: "title", "alias", "tags", "keywords" and "summary". Punctuation and duplicate words are removed, as are a short list of stop words. Basically if you want the page to be found using a word that isn't in the usual metadata, just create a list in the "keyword" metadata.

> NOTE: Originally I referred to this project as "fake wiki". Then I though it was more like a  "mock wiki", and in a fit of alliterative humour I changed the project to "mokuwiki" in homage to *DokuWiki*. This should not be construed as "mocking" *DokuWiki*---far from it! *DokuWiki* is a great piece of software---if you need a proper wiki use that, don't use this!

# Installation

Download and unzip the latest distribution, e.g. `dist/mokuwiki-1.0.0.zip` file. Unzip it, change to the "mokuwiki-1.0.0" folder and run the install command:

```
$ cd mokuwiki-1.0.0
$ python setup.py install
```

# Usage

Once installed as above then just run "mokuwiki" as a module from the command line:

```
$ python -m mokuwiki input-dir output-dir
```

Run in a Python interpreter using the "mokuwiki()" function:

```
$ python
>>> import mokuwiki
>>> mokuwiki.mokuwiki(input_dir, output_dir)
```

Run `mokuwiki --help` for all options.

# Assumptions

1.  [pandoc](pandoc.org) is being used as the Markdown processor (or at least, some converter that supports the `pandoc` Markdown syntax). The processor will need YAML metadata support and bracketed
spans, at the very least.

# Caveats

1.  This is my first Python project (yay!), so it's mostly been cobbled together from Stack Overflow answers, mostly. As a result it's probably not what you'd call Pythonic but it does what it's supposed to do..
2.  Error checking/handling is minimal/probably woefully inadequate.
3.  There are some things you can't do (brackets in titles etc) that could probably be addressed by better regular expressions or a more complete model of what I think it should be doing.
4.  `mokuwiki` only converts the page link, tag list, file include and image link markup into the equivalent Markdown---adding any other features to the resultant HTML will have to be done by say, a `pandoc` template or similar mechanism. Regular Markdown syntax should be preserved.
5.  You cannot have two pages with the same title/alias (which actually kind of makes sense, for a wiki).
6.  The image link markup... to be honest this was just because it was easy to do! I'm not sure if it really worth it but you can always ignore it and put images in normally.

# To Do

1.  Better error handling.
2.  More efficient file I/O. Currently each file is read once to create the index, then they are all read again so that the tag links can be resolved. There may be a more efficient way to do this using a database, or some other new-fangled doohickey, but in tests the time taken for the script to run is negligable compared to the "conversion to HTML" step.
3.  Replace the complex namespace/show name/page name logic with a suitable regular expression.
4.  Replace the complex logic that handles special tag characters (e.g. "{{@}}") with something more elegant.
5.  The search index is not really optimised for search---if anything it's optimised for the size of the file. But again, in tests on 250 pages, there is no noticeable delay in displaying the results with a simple Javascript function so...
