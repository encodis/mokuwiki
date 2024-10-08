# Introduction

For a while I've been running the excellent [DokuWiki](https://www.dokuwiki.org) on my Mac using OS X's bundled Apache server. The problem is that every time Apple update the OS they futz with the Apache config, so I have to work out how to get it going again. Then I have to update `DokuWiki` itself, as I don't do that nearly as often as I should. Etc, etc.

However, it struck me that I don't really need a wiki as such---all I really need for my purposes are inter-page links (within pages in the same folder, usually) and the ability to tag pages and then get lists of pages that match a given set of tags. (This is basically DokuWiki's double bracket syntax for links to another page -- `[[A Page Title]] ` -- and its [tag](https://www.dokuwiki.org/plugin:tag) plugin.) I don't actually need the "wiki" bit, as I can easily edit the files locally and compile/deploy as needed. I've also got used to using Markdown rather than DokuWiki's markup (although there is a Markdown plugin for that but it's not Pandoc Markdown, which I prefer... and so on and so on).

So this project hosts a Python script (`mokuwiki.py`) that takes a source folder of Markdown documents and processes them according to a number of directives, putting the results in a target folder. The files in this target folder can then processed by a Markdown engine (such as [Pandoc](https://pandoc.org)) as usual. For my 'wikis' I usually use the 'single file' mode and Pandoc's standalone option on each file to produce the individual HTML pages (so in that respect it's a bit like part of a static site generator), but you can also run MokuWiki on a single file to take advantage of useful directives like file includes or comments.

> NOTE: Originally I referred to this project as "fake wiki" which led to "mock wiki", and in a fit of alliterative humour I changed the project to "mokuwiki" in homage to *DokuWiki*. This should not be construed as "mocking" *DokuWiki*---far from it! *DokuWiki* is a great piece of software---if you need a proper wiki use that, don't use this!

# Usage

this will be basic operations and the general idea, source to target etc.

# Wiki Configuration File

This version (v2.0 and greater) of `mokuwiki` supports multiple namespaces and many more configuration options. Consequently the configuration has been moved from the command line to a configuration file, a full example of which is shown below:

```
# Sample MokuWiki configuration file

[DEFAULT]
wikiname = My Wiki
verbose = 1
target = build
media_dir = images
broken_css = .broken
tags_css = .tags
custom_css = .smallcaps
search_fields = title,alias,tags,summary,keywords
search_prefix = 
search_file = _index.json
meta_fields = tags
noise_words = x,y,z
# noise_words = file:noise.txt

[Namespace 1]
name = namespace1
alias = ns1
path = ./folder1/pages
noise_tags = xxx,yyy,zzz
```

A __wiki__ is composed of one or more __namespaces__; each namespace contains a number of __pages__. The folder containing the configuration file is assumed to be the root folder. Each namespace is in a sub-folder of this root folder, with the folder name given by the `path` configuration option for that namespace. So in the example above the pages for the namespace called "Namespace 1" live in the `folder1/pages` folder. Once processed these files will end up in the `build/namespace1` folder --- the wiki options set the base target and the namespace's `name` sets the folder name within that. 

## Wiki Options

Note that these options will be applied as the default for all namespaces, but individual namespaces can override them by including that optin in their own section.
### name

The name of the wiki. Currently this is not used in the page processing.

### verbose

How verbose to make the output. This takes a value from 1 to 3 (most verbose).

### target

The base target folder. All namespaces will be created under this folder. The default target is "build".

### media_dir

The name of the media directory to include in image links. The default is `images`, i.e. it is assumed that all images that belong to a namepsace will be placed in an "images/" sub-folder.

### broken_css

The CSS used to identify a "broken" link, i.e. when a page link does not exist. The default is `.broken`, implying that once the processed files are rendered from Markdown to HTML there will be a CSS definition for that CSS.

### tags_css

The CSS used to identify a "tag" link, which is produced by the `{{#tag}}` directive. The default is `.tag`. Again, the actual CSS defintion should be available to the final HTML.

### custom_css

The CSS used to identify a "custom" link, which is produced by the `^^some text^^` directive. The default is `.smallcaps` which must be available to the final HTML. Note that `pandoc` provides a default value for this in its default template.

### search_fields

The metadata fields used to build the search index. This is a comma separated list of keywords. The default is `title,alias,tags,summary,keywords`. The pseudo-keyword `_body_` can also be used to index the body of the file. To turn off generation of a search index leave this field empty, or use the `--nosearch` command line option.

Note that this is customisable for each namespace.

### search_prefix

The search index is a JSON file that can be included in a web page. To facilitate this the `search_prefix` will be prepended to the output so that the file can be included as a JSON object. For example, the author uses `var MW = MW || {}; MW.searchIndex = ` as the prefix to faciliate direct inclusion of a search index.

### search_file

The name of the search index file. The default value is "_index.json". Note that search indexes are created for and are specific to an individual namespace.

### meta_fields

In some cases it is useful to convert some metadata fields into page links. A good example of this is when tags are used and displayed by the resulting HTML file. 

### noise_words

A comma separated list of words to ignore when building the search index. If the value of this options starts with the string "file:" then the remainder of the string will be assumed to be a plain text file containing a list of noise words (one word per line). If so this file will be read and used instead. The default is a list of common noise words.

### templates

TODO for file includes/tags - can have NS level too 

# How it works

MokuWiki makes two key assumptions about the files that it processes:

1.   YAML metadata elements in each source file control how it is processed. Most importantly this includes the name of the resulting file in the target folder (the 'title' element, see below). 

2.  Directives are processed once to yield Markdown files that will then be processed by some other application (the assumption is Pandoc, or something that understands Pandoc flavoured Markdown as that is what MokuWiki emits).

## Metadata

All YAML metadata elements are passed through to the output files in the target folder unchanged. However, the presence of the following metadata will have the indicated result:

*   *title*: The page's title is used to link to it using a 'page link' directive in another page (see below). It is also used to create the file name for that page in the target folder (see [Filename conversion] below). Titles must be unique within the source folder. 

*   *alias*: Aliases are also used to link to a page as an alternative to using a page's title. This can be useful if the actual title that is to be displayed (the "formal" title, if you will) is long but has a common shorter form. Aliases must be unique and not the same as any title.

*   *tags*: A YAML sequence of strings that represent what the page is about, e.g. '[vehicle, equipment]'

For example, if this is the contents of `file1.md`:

```
---
title: Page One
alias: 1st Page
author: Phil
tags: [abc]
...

A link to [[Page Two]]

```

and this is `file2.md`

```
---
title: Page Two
author: Phil
tags: [abc]
...

A link to [[Page One]]

A link to [[1st Page]]

```

then MokuWiki will create two files in the target folder. Based on their titles these will be `page_one.md` and `page_two.md` in the target folder. The page link directives (the double square brackets) will become, in `page_two.md` for example:

```
---
title: Page Two
author: Phil
tags: [abc]
...

A link to [Page One](page_one.html)

A link to [1st Page](page_one.html)

```

> NOTE: The YAML metadata block must start with three dashes and end with three periods. 

## Directives

The following directives are supported within a page. These generally take the form of double characters (often brackets) that should be unrecognised by a Markdown processor. 

### Page links

As described above links between pages are specified using double square brackets, so `[[Page One]]` is converted to a standard Markdown link to the HTML version of the page with that title: `[Page One](page_one.html)`. If a page has an alias then that can be used instead of the title, although the link name is still based on the title: `[[1st Page]]` becomes `[1st Page](page_one.html)`. 

You can also define a "display" name using the syntax `[[Display Name|Page One]]`. This will become `[Display Name](page_one.html)` in the target file. Note that unlike the similar DokuWiki syntax you cannot specify an actual filename here: that is always determined by the 'title' metadata. 

Note that MokuWiki assumes that the eventual output will be HTML, so all of the links end in ".html".

If a page does not have a 'title' field in the metadata block (or no metadata block at all) then processing of that file is skipped. The 'title' also cannot contain parentheses or brackets (basically just alpha-numeric characters and some punctuation)---see the section on [Filename Conversion] below.

Page link directives that link to a non-existent page are transformed into bracketed spans with the 'broken' class. That is, `[[No Such Page]]` will be converted to `[No Such Page]{.broken}`. Use the `--broken` command line option to change the class name used for broken links. Use the `--report` command line option to list all broken links (i.e. missing pages) on standard out once processing is complete.

#### Namespaces 

Page names can contain references to namespaces, again based on the MoukWiki model, e.g. `[[ns1:Page One]]`. Namespaces are assumed to refer to folders and so cannot contain spaces. How these are incorporated into the resulting link depends on whether the `--fullns` command line option is set:

1.  When not set (the default) it assumes that the source folder is the main folder, with a single level of child folders, e.g. "source/ns1", "source/n2" and so on. A page link with a namespace reference in a page in the folder "source/ns1" is assumed to point to a page in a sibling folder. Therefore a page link directive like `[[ns2:Page Two]]` in a document in "source/ns1" will convert to `[Page Two](../ns2/page_two.html)`.
    
2.  When `--fullns` is set it will treat a namespace as a full path of folders. The author is then responsible for specifying the correct relative path, e.g. `[[..:..:ns2:ns3:Some Page]]` will become `[Some Page](../../ns2/n3/some_page.html)`.

> NOTE: MokuWiki does **not** recursively process folders and keep track of namespaces. This functionality merely makes it easier to create links between pages in different folders. Note also that this functionality may change in future versions...

### Image links

The image link directive provides an easier way to link to images: the syntax `!!A Nice Image!!` will be converted to `![A Nice Image](images/a_nice_image.jpg)`. Some points to note include:

1.  The name of the link ('A Nice Image' in the example) is also the name of the image's caption.
2.  The default assumes that all images are in an `images` folder which is a child of the folder the referencing file is in. The folder name can be changed with the `--media` command line option. 
3.  The default file format assumed is JPEG, therefore the extension is '.jpg'. This can be changed using the following syntax: `!!Another Picture|png!!`.
4.  MoukWiki will not check for the existence of the 'image' folder or move any images into the target folder.

### Exec directives

The 'exec' directive allows the output of a command can be inserted into the document using the following syntax: `%% ls -l test/*.dat %%`. The command must be in the user's PATH and any file specifications that the directive is to glob must be the last element of the command line (as shown here). Multiple, semi-colon separated commands are supported.

1.  This directive uses the [subprocess.run()](https://docs.python.org/3/library/subprocess.html#subprocess.run) function. Therefore [standard security considerations](https://docs.python.org/3.6/library/subprocess.html#security-considerations) should be borne in mind when using this feature.
2.  This feature has not been checked on Windows machines, but should work if executed in the appropriate shell (e.g. Git Bash).
3.  The output of the command should be text suitable for a Markdown file.

### Custom style

The custom style directive provides a way to wrap text in a custom style using Pandoc's [bracketed span](https://pandoc.org/MANUAL.html#divs-and-spans) feature: the syntax `^^styled text^^` will give an output of `[styled text]{.smallcaps}`, i.e. the default Pandoc command for small caps. The style can be changed using the `--custom` flag on the command line. The text of this argument is copied directly into CSS portion of the span, so should include the leading "dot" if it is to be a CSS class. 

Note that this directive is processed last, so it will apply the custom style to links (e.g. `^^[[Page One]]^^` will work as expected).

### Comment directives

Single line comments can be included in a source file: any characters on the line that occur after a double slash followed by a space (`// `) will be removed. There are no block comments. 

### Tag directives

Tags that have been created by a page can be referenced in any page using the following syntax: `{{tag1}}`. This will produce a list of page links that have the "tag1" tag. So, for example, a source fragment:

```
Pages containing tag 'abc':

{{abc}}
```

might produce:

```
Pages containing tags 'abc':

[Page One](page_one.html)

[Page Two](page_two.html)
```

Tag names cannot contain brackets or punctuation. When being defined in the YAML block tag names can contain spaces, e.g. `tags: [Wordy Tag, Other Tag]`. However, when referencing tags with spaces you must use an underscore instead of a space, e.g. `{{Wordy_Tag +other_tag}}`. Tag names are case-insensitive.

Tags can be combined using various operators:

1.  `{{tag1 tag2}}` includes pages with 'tag1' *or* 'tag2'
2.  `{{tag1 +tag2}}` includes pages with 'tag1' *and* 'tag2'
3.  `{{tag1 -tag2}}` includes pages with 'tag1' that do *not* have 'tag2'
4.  `{{*}}` includes *all* pages in the wiki that have any tag. Note that pages do not have to have a `tags` fields.
5.  `{{#}}` represents the number of pages that have any tag
6.  `{{#tag1}}` represents the number of pages that have the tag 'tag1'
7.  `{{@}}` will return a list of all tags defined in the source folder as a series of bracketed spans with the class name 'tag'. This can be used to style tag lists. The class name can be changed using the `--tag` command line option.

By default, the list of pages returned is restricted to the current namespace. A different namespace can be specified using the following format: `{{ns1:tag1}}`. Only the first tag can have a namespace specified. For example, to include all pages in the namespace `ns1` with `tag1` and `tag2` you would use `{{ns1:tag1 +tag2}}`.

The tag directives supports a number of options. These can be added (in any order) after the last tag specification, for example `{{tag1 -tag2 --sort}}`

The options available are:

-  `--sort`: Sort the included page list alphabetically
-  `--sep S`: Add the string S between each page. Default is ''.
-  `--format T`: Instead of a link to the page being output, the string T is used as a template for the output text. 
-  `--header T`: Output this string or template before any page information. This is useful when making a Markdown table.
-  `--before S`: Add the string S before each page output. Default is `\n`
-  `--after S`: Add the string S after each page output. Default is `\n`

Note that templating (see below) can be applied to the `format` and `header` options


### Include directives

Include the contents of one file in another using the following markup: `<<include_me.md>>`. Any YAML data blocks (i.e. metadata) will be removed from the included file before inclusion (although they *will* be parsed, so metdata elements can be used in format and header templates). This pattern actually supports globbing, so you can do `<<include_X*Y.dat>>` and so on. The path is assumed to be relative to the directory that the module was invoked from.

The include directive supports a number of options. These can be added (in any order) after the path specification, for example `<<fileX*.md --sort>>`.

The available options are:

-  `--sort`: Sort the included page list alphabetically
-  `--sep S`: Add the string S between each page. Default is ''.
-  `--shift N`: Shift all headers in the included page "up" by one (so that "# Heading" becomes "## Heading"). The default is 0, and negative numbers are supported.
-  `--indent S`: Add the string S before each line of the included content. For example, `<<fileX.md --indent "> ">>` would transform the included content from "fileX.md" into a block quote.
-  `--format T`: Instead the page content being output, the string T is used as a template for the output text. 
-  `--header T`: Output this string or template before any page content. This is useful when making a Markdown table.
-  `--before S`: Add the string S before each page output. Default is `\n`
-  `--after S`: Add the string S after each page output. Default is `\n`
-  `--repeat N`: Add the content N times. Default is 1, the maximum is 999.


### Templating and metadata substitution

The tag and include directives are actually very similar, the main differenmt beign that the former includes ocnmtent by tga and the latter by file name/path. Also the default content for tags is a liong to the page, but for includes it is the page conettm. Both directives suppoert the format and header options, whihc can make extensivbe use of templates specified in the Wiki config.

Blank lines will be inserted between the contents of each file, and separators can be inserted between each one by using the syntax `<<include_X*Y.dat|* * *>>`. (The default is no separator, but "* * *" is a useful one as it becomes a horizontal rule when processed by `pandoc`. )

A prefix can also be inserted in front of each *line* of the included files by specifying it as a third 'argument'. For example, `<<include_X*Y.dat|* * *|> >>` will insert `> ` in front of each line, thereby including the content of the file as a block quote. To do so without a separator between files just leave that argument empty: `<<include_X*Y.dat||> >>`.

Although the metadata section of each included file is discarded, it *is* parsed. This allows MokuWiki to substitute those metadata values into the body of the included file using certain placeholders: `?{value}` or just `?value`. (The former is preferred to reduce ambiguity.) For example, to include the date (assuming there is such a metadata) field, you would have the text "this is the ?{date}" in the file body. This behaviour is on by default, but can be turned off using the `-R` or `--replace` flags.

Two specific metadata fields are also recognized. If either (or both) of the fields `prefix` or `suffix` are present they will be prepended/appended to the file's content before further processing. In essence, these act as though the directives `?{prefix}` and `?{suffix}` were embedded in the body of the file.

EXAMPLES OF PREFIX, SUFFIX

options are

sort
sep
shift
indent
before: before and after each file
after
header: at start of whole include
format
repeat

### Paths etc


## Other features

### Single file mode

Single file mode can be enabled with the `--single` option. Only a single input file is expected and the output file given on the command line is used 'as-is' for the output (i.e. is assumed to be the intended output file name). This is not very useful for page links and tags but can be very handy for using the 'include' and 'exec' directives in the specified input file. The [search index] option is disabled in single file mode.

### Search index

The optional command line option `--index` will cause MokuWiki to output a JSON file (called '_index.json') which contains an inverted index of terms contained in each page against page titles and file names. This can be used to create a simplistic search function in the "wiki". This is in JSON format:

```
{
    "page": [
        ["page_one", "Page One"],
        ["page_two", "Page Two"]
    ],
    "abc": [
        ["page_one", "Page One"],
        ["page_two", "Page Two"]
    ],
    "one": [
        ["page_one", "Page One"]
    ],
    "two": [
        ["page_two", "Page Two"]
    ]
}
```

To include this directly in an HTML page using a `<script>` statement it is often convenient to have this declared as a variable. Use the `--prefix` option to prefix the JSON with a string. For example, the author uses `--prefix='var MW = MW || {}; MW.searchIndex = '` on one of his projects for this purpose.

### Search index fields

By default the following YAML metadata fields are parsed to create the search index: 'title', 'alias', 'summary', 'tags' and 'keywords'. A source file that has a metadata field of 'noindex' set to 'true' will *not* be indexed. Use the `--fields` option to specify a different list, e.g. `--fields='title,author'`.

The contents of files (i.e. the body text, after the metadata) can be indexed by using a "pseudo-field" called `_body_`. All punctuation etc. is removed from the indexed terms. 

### Noise words

A small list of 'noise words' is included in MokuWiki by default. These are not indexed if they occur in any of the chosen metadata fields. The list can be changed using the `--noise` option to supply a plain text file of words, with one word on each line. For example, `--noise=bad_words.txt`.

### Filename conversion

Target file names are created from the 'title' field as follows: leading and following spaces are stripped, remaining spaces are replaced with underscores and the whole string is made lower case. Unicode characters are also removed.

# Installation

As MokuWiki is available on [PyPi](https://pypi.org) installation should be as simple as:

```
$ pip install mokuwiki
```

`mokuwiki` is dependent on [PyYAML](https://pyyaml.org). Some of the unit tests are dependent on [DeepDiff](https://github.com/seperman/deepdiff). 
    
# Usage

Once installed `mokuwiki` should be available as a command line script:

```
$ mokuwiki source-dir target-dir
```

or it can be run as a standard Python module:

```
$ python -m mokuwiki source-dir target-dir
```

Run in a Python interpreter using the "mokuwiki()" function:

```
$ python
>>> import mokuwiki
>>> mokuwiki.mokuwiki(source_dir, target_dir)
```

Run `mokuwiki --help` for all options.


# Caveats

1.  You cannot have two pages with the same title/alias (which actually kind of makes sense, for a wiki).
2.  `mokuwiki` only converts the directive markup into the equivalent Markdown---adding any other features to the resultant HTML will have to be done by say, a `pandoc` template or similar mechanism. Regular Markdown syntax should be preserved.
3.  This is started as one of my first Python projects, so it's mostly been cobbled together from Stack Overflow answers, mostly. It also designed mainly for my specific needs although I have tried to generalise it where I could. It seems to work alright but I wouldn't use it in production without some careful thought...

# To Do

1.  Better error handling.
2.  More efficient file I/O. Currently each file is read once to create an index, then they are all read again so that the tag links can be resolved. There may be a more efficient way to do this using a database, or some other new-fangled doohickey, but in tests the time taken for the script to run is negligible compared to the "conversion to HTML" step.
3.  Replace the current namespace mechanism with something modelled on *DokuWiki*'s.
4.  Replace the complex logic that handles special tag characters (e.g. "{{@}}") with something more elegant.


# Development notes

## Unit testing

A number of unit tests are included in the `tests` folder and can be run using the [pytest](https://pypi.org/project/pytest/) application.

## Packaging a distribution

When ready for a release use the [bumpversion](https://pypi.org/project/bumpversion/) application to update the version number, e.g.

```
$ bumpversion major --tag
```

This will update the source file and the setup configuration. Then build the distribution:

```
$ python setup.py bdist_wheel
```

## Testing installation

Testing that the distribution installs correctly can be accomplished using Docker. Use the following command (which will download the "python" Docker image if necessary, so it might take a couple of minutes when first run):

```
$ docker run -it --rm -v "$PWD":/mnt python bash
```

This will start the "python" Docker image and execute a command prompt. From here install the "mokuwiki" distribution from the local "dist" folder (mounted in the Docker image under "/mnt"). Note that you have to install the dependency ([pyyaml](https://pypi.org/project/PyYAML/)) first as "--no-index" is specified.

```
root@382a37174524:/# pip install pyyaml
root@382a37174524:/# pip install mokuwiki --no-index --find-links /mnt/dist
root@382a37174524:/# mokuwiki -h
root@382a37174524:/# python
>>> import mokuwiki
>>> exit()
```

## Upload to TestPyPi

Upload the distribution to the TestPyPi site:

```
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Then run the "python" Docker image and attempt to install from there:

```
$ docker run -it -v "$PWD":/mnt --entrypoint=bash python
root@382a37174524:/# pip install --extra-index-url https://pypi.org --index-url https://test.pypi.org/simple/ mokuwiki
root@382a37174524:/# mokuwiki -h
```

## Upload to PyPi

Upload to the real package index as follows (or specify the latest distribution):

```
$ twine upload dist/*
```
