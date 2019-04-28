# Introduction

For a while I've been running the excellent [DokuWiki](https://www.dokuwiki.org) on my Mac using OS X's bundled Apache server. The problem is that every time Apple update the OS they futz with the Apache config, so I have to work out how to get it going again. Then I have to update `DokuWiki` itself, as I don't do that nearly as often as I should. Etc, etc.

However, it struck me that I don't really need a wiki as such---all I really need for my purposes are inter-page links (within pages in the same folder, usually) and the ability to tag pages and then get lists of pages that match a given set of tags. (This is basically DokuWiki's double bracket syntax for links to another page -- `[[A Page Title]] ` -- and its [tag](https://www.dokuwiki.org/plugin:tag) plugin.) I don't actually need the "wiki" bit, as I can easily edit the files locally and compile/deploy as needed. I've also got used to using Markdown rather than DokuWiki's markup (although there is a Markdown plugin for that but it's not Pandoc Markdown... and so on and so on).

So this project hosts a Python script (`mokuwiki.py`) that takes a source folder of Markdown documents (or a folder with a file specification) and processes them according to a number of directives, putting the results in a target  folder. The files in this target folder can then processed by Pandoc as usual. For my 'wikis' I usually use the 'single file' mode and Pandoc's standalone option on each file to produce the individual HTML pages, but you can also run MokuWiki on a single file to take advantage of useful directives like file includes or comments.

> NOTE: Originally I referred to this project as "fake wiki". Then I though it was more like a  "mock wiki", and in a fit of alliterative humour I changed the project to "mokuwiki" in homage to *DokuWiki*. This should not be construed as "mocking" *DokuWiki*---far from it! *DokuWiki* is a great piece of software---if you need a proper wiki use that, don't use this!

MokuWiki makes two key assumptions about the files that it processes:

1.   YAML metadata elements in each source file control how it is processed. Most importantly this includes the name of the resulting file in the target folder (the 'title' element, see below). 
2.  Directives are processed once to yield Markdown files that will then bprocessed by some other application (the assumption is Pandoc, or something that understands Pandoc flavoured Markdown as that is what MokuWiki emits).

## Metadata

All YAML metadata elements are passed through to the output files in the target folder unchanged. However, the presence of the following metadata will have the indicated result:

*   *title*: The page's title is used to link to it using a 'page link' directive in another page (see below). It is also used to create the file name for that page in the target folder. Titles must be unique within the source folder. 

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

Then MokuWiki will create two files in the target folder. Based on their titles these will become `page_one.md` and `page_two.md` in the target folder. The page link directives (the double square brackets) will become, in `page_two.md` for example:

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

The following directives are supported within a page. These generally take the form of 

### Page Links

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

### Tag Links

Tags that have been can be referenced in a page using the following syntax: `{{tag1}}`. This will produce a list of page links that have the "tag1" tag. So, for example, a source fragment:

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

### Include Directive

Include one file in another using the following markup: `<<include_me.md>>`. Any YAML data blocks will be removed from the included file before inclusion. This pattern actually supports globbing, so you can do `<<include_X*Y.dat>>` and so on. The path is assumed to be relative to the directory that the module was invoked from.

Blank lines will be inserted between the contents of each file, and separators can be inserted between each one by using the syntax `<<include_X*Y.dat|* * *>>`. (The default is no separator, but "* * *" is a useful one as it becomes a horizontal rule when processed by `pandoc`. )

A prefix can also be inserted in front of each *line* of the included files by specifying it as a third 'argument'. For example, `<<include_X*Y.dat|* * *|> >>` will insert `> ` in front of each line, including the content of the file as a block quote. To do so without a separator between files just leave that argument empty: `<<include_X*Y.dat||> >>`.

### Image Links

The image link directive provides an easier way to link to images: the syntax `!!A Nice Image!!` will be converted to `![A Nice Image](images/a_nice_image.jpg)`. Some points to note include:

1.  The name of the link ('A Nice Image' in the example) is also the name of the image's caption.
2.  The default assumes that all images are in an `images` folder which is a child of the folder the referencing file is in. The folder name can be changed with the `--media` command line option. 
3.  The default file format assumed is JPEG, therefore the extension is '.jpg'. This can be changed using the following syntax: `!!Another Picture|png!!`.
4.  MoukWiki will not check for the existence of the 'image' folder or move any images into the target folder.

### Exec Links

The 'exec' directive allows the output of a command can be inserted into the document using the following syntax: `%% ls -l test/*.dat %%`. The command must be in the user's PATH and any file specifications that the directive is to glob must be the last element of the command line (as shown here). Multiple, semi-colon separated commands are supported.

1.  This directive uses the [subprocess.run()](https://docs.python.org/3/library/subprocess.html#subprocess.run) function. Therefore [standard security considerations](https://docs.python.org/3.6/library/subprocess.html#security-considerations) should be borne in mind when using this feature.
2.  This feature has not been checked on Windows machines, but should work if executed in the appropriate shell (e.g. Git Bash).
3.  The output of the command should be text suitable for a Markdown file.

### Comment Directives

Single line comments can be included in a source file: any characters on the line that occur after a double slash (`//`) will be removed. There are no block comments. 

## Other Features

### Single File Mode

Single file mode can be enabled with the `--single` option. Only a single input file is expected and the output file given on the command line is used 'as-is' for the output (i.e. is assumed to be the intended output file name). This is not very useful for page links and tags but can be very handy for using the 'include' and 'exec' directives in the specified input file. The [search index] option is disabled in single file mode.

### Search Index

The optional command line option `--index` will cause MoukWiki to output a JSON file (called '_index.json') which contains an index of titles, file names and terms contained in each page. This can be used to create a simplistic search function in the "wiki". This has the format:

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

It is assumed that this file will be included using a `<script>` statement so to be accessible it needs to be in a variable. The default string prefixed to the index is the one the author uses. This can be changed using the `--prefix` option (use an empty string to remove it entirely.) A small list of 'stop words' is included in MokuWiki and these are removed. 

The following YAML metadata fields are parsed to create this index: 'title', 'alias', 'summary', 'tags' and 'keywords'. A file that has a metadata field of 'noindex' set to 'true' will *not* be indexed. 

The `--invert` option will produce an inverted index, which is arguably more useful (or at least more efficient). This has the following format, where each term is followed by a list of 'page name' and 'title' pairs. 
:

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

### Filename Conversion

Target file names are created from the 'title' field as follows: leading and following spaces are stripped, remaining spaces are replaced with underscores and the whole string is made lower case. Unicode characters are also removed.

# Installation

As MokuWiki is available on [PyPi](https://pypi.org) installation should be as simple as:

```
$ pip install mokuwiki
```

There are no dependencies to install (although there are if you want to clone the repo and run the test files).
    
# Usage

Once installed as above then just run "mokuwiki" as a module from the command line:

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

1.  This is my first Python project (yay!), so it's mostly been cobbled together from Stack Overflow answers, mostly. As a result it's probably not what you'd call Pythonic but it does what it's supposed to do..
2.  Error checking/handling is minimal/probably woefully inadequate.
3.  There are some things you can't do (brackets in titles etc) that could probably be addressed by better regular expressions or a more complete model of what I think it should be doing.
4.  `mokuwiki` only converts the directive markup into the equivalent Markdown---adding any other features to the resultant HTML will have to be done by say, a `pandoc` template or similar mechanism. Regular Markdown syntax should be preserved.
5.  You cannot have two pages with the same title/alias (which actually kind of makes sense, for a wiki).
6.  The image link markup... to be honest this was just because it was easy to do! I'm not sure if it really worth it but you can always ignore it and put images in normally.

# To Do

1.  Better error handling.
2.  More efficient file I/O. Currently each file is read once to create an index, then they are all read again so that the tag links can be resolved. There may be a more efficient way to do this using a database, or some other new-fangled doohickey, but in tests the time taken for the script to run is negligable compared to the "conversion to HTML" step.
3.  Replace the complex namespace/show name/page name logic with a suitable regular expression. In fact, have a better namespace system modelled on *DokuWiki*'s.
4.  Replace the complex logic that handles special tag characters (e.g. "{{@}}") with something more elegant.

