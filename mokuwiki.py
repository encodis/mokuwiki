#!/usr/bin/env python

"""mokuwiki.py

note on what yaml metadata is assumed

A module that copies a folder of Markdown files to another folder, applying the following transforms to each file based on text patterns found in the source files:

- `[[A Page Title]]`. A link to another page in the same namespace. This will be converted to `[A Page Title](a_page_title.html)`. Page titles are determined by the 'title' element of a page's YAML metadata block using the same algorithm as the link generator.

- `{{tag...}}`. A series of paragraphs, each containing a link to a page (as above) that has a tag or tags that matches the tag specification. This can include:
    -  `{{tag1}}` lists all pages with 'tag1'
    -  `{{tag1 tag2}}` lists all pages with 'tag1' or 'tag2'
    -  `{{tag1 +tag2}}` lists all pages with 'tag1' and 'tag2'
    -  `{{tag1 -tag2}}` lists all pages with 'tag1' that do not have 'tag2'
    -  `{{*}}` list all pages that have any tag at all
    -  `{{#}}` the total number of pages
    -  `{{#tag}}` the total number of pages with 'tag'
    -  `{{@}}` a list of all tags (output as bracketed spans with a class of 'tag')

-  `<<file...>>`. Include the specified file(s) at that point in the current file. Any YAML metadata blocks are removed before inclusion. Wildcards are supported and a separator line can be added between each file (but not after the last file):
    -  `<<include_file.md>>` includes the *include_file.md* file
    -  `<<../data/xyz*.md>>` includes all Markdown files in the sibling *data* folder that start with *xyz*
    -  `<<../data/xyz*.md|* * *>>` as above, but adds the line "* * *" between each one (which with Pandoc becomes a horizontal rule)
    -  `<<../data/xyz*.md|* * *|> >>` as above, adding the line "* * *" between each one and prefacing each line with the characters *> * (i.e. the Markdown markup for "blockquote")
    -  `<<../data/xyz*.md||NOTE:>>` includes the files with no separator between then, prefixing each line with "NOTE:"

- `!!Image Name!!`. A link to an image. This will be converted to `![Image Name](images/image_name.jpg)`. Images are assumed to live in an **images** folder local to the namespace but this can be changed with the `--media` command line option. Other options include:
    -  `!!Image Name|png!!` changes the extension to ".png"

-  `%%command...%%`. The output of the command specification is inserted into the file. File globbing is supported as long as it is at the end of the line, e.g. `%% ls -l test/*.md %%`, or `%% awk '/^title:/ {$1=""; gsub(/^[ \t]+/,"",$0); gsub(/[ \t]+$/,"",$0); print "["$0"]\n"}' sections/*.md %%`





Output files can then be processed using a Markdown processor (the assumption is that 'pandoc' is
being used).

NOTE: The files in the specified output folder are named according to their title (not their input
file name). For example, a page called "file1.md" with the "title" metadata equal to "A Page Title"
will be converted to "a_page_title.md".

NOTE: Using the '--index' option will also output a "_index.json" file that contains a JSON object
that might be useful for use by a search function in a webpage.

NOTE: The '--single' option will invoke single file mode. Only one input file can be specified, and
the output target will be used for the output file 'as is'. Single file mode will turn off the
'--index' option, if enabled.

"""

import os
import re
import json
import glob
import argparse
import subprocess
import shlex


###

def mokuwiki(source, target,
             single=False, index=False, invert=True, report=False, fullns=False,
             prefix='var MW = MW || {};\nMW.searchIndex = ', broken='broken', tag='tag', media='images'):

    # configure
    # TODO config object not available if this was imported? but tests work OK?
    config.source = source
    config.target = target
    config.single = single
    config.index = index
    config.invert = invert
    config.report = report
    config.fullns = fullns
    config.prefix = prefix
    config.broken = broken
    config.tag = tag
    config.media = media

    # default file spec
    file_spec = "*.md"

    # check source folder
    if not os.path.isdir(config.source):
        # not a dir, so first assume a file spec also given
        config.source, file_spec = config.source.rsplit(os.sep, 1)

        # CHECK do we really want a filespec allowed outside of single file mode?
        # now check again
        if not os.path.isdir(config.source):
            print(f"mokuwiki: source folder '{config.source}' does not exist or is not a folder")
            exit()

    # get list of input files
    file_list = glob.glob(os.path.normpath(os.path.join(config.source, file_spec)))

    # check single file mode configuration
    if config.single:

        # cannot generate search index in single file mode
        config.index = False

        if len(file_list) > 1:
            print("mokuwiki: single file mode specified but more than one input file found")
            exit()

    else:

        if not os.path.isdir(config.target):
            print(f"mokuwiki: target folder '{config.target}' does not exist or is not a folder")
            exit()

    # first pass - create indexes
    create_indexes(file_list)

    # second pass - process files
    process_files(file_list)

    # show list of broken links
    if config.report:
        print('\n'.join(sorted(page_index["broken"])))

    # write out search index (unless in single file mode)
    if config.index:
        search_index = config.prefix + json.dumps(page_index["search"], indent=2)

        with open(os.path.join(config.target, "_index.json"), "w", encoding="utf8") as json_file:
            json_file.write(search_index)


###

def create_indexes(file_list):
    """Create all relevant indexes

    Args:
        file_list (list): list of files to be indexed

    Returns:
        None
    """

    # reset page indexes
    reset_page_index()

    # create all indexes
    for file in file_list:

        with open(file, "r", encoding="utf8") as input_file:
            contents = input_file.read()

        # get title
        title = parse_metadata("title", contents)

        if not title:
            continue

        if title not in page_index["title"]:
            page_index["title"][title] = create_valid_filename(title)
        else:
            print(f"mokuwiki: skipping '{file}', duplicate title '{title}'")
            continue

        # get alias (if any)
        alias = parse_metadata("alias", contents)

        if alias:
            if alias not in page_index["alias"] and alias not in page_index["title"]:
                page_index["alias"][alias] = title
            else:
                print(f"mokuwiki: duplicate alias '{alias}', in file '{file}'")

        # get list of tags (if any)
        tags = parse_metadata("tags", contents)

        if not tags:
            continue

        # add each tag to index, with titles as set
        for tag in tags:

            # strip end spaces and convert to lower case
            tag_name = tag.strip().lower()

            if tag_name not in page_index["tags"]:
                page_index["tags"][tag_name] = set()

            page_index["tags"][tag_name].add(title)


###

def process_files(file_list):
    for file in file_list:

        with open(file, "r", encoding="utf8") as input_file:
            contents = input_file.read()

        title = parse_metadata("title", contents)

        if not title:
            print(f"mokuwiki: skipping '{file}', no title found")
            continue

        # replace file transclusion first (may include tag and page links)
        contents = regex_link["file"].sub(convert_file_link, contents)

        # replace exec links next
        contents = regex_link["exec"].sub(convert_exec_link, contents)

        # replace tag links next (this may create page links, so do this before page links)
        contents = regex_link["tags"].sub(convert_tags_link, contents)

        # replace page links
        contents = regex_link["page"].sub(convert_page_link, contents)

        # replace image links
        contents = regex_link["image"].sub(convert_image_link, contents)

        # get output file name by adding ".md" to title's file name
        if config.single:
            output_name = config.target
        else:
            output_name = os.path.join(config.target, page_index["title"][title] + ".md")

        with open(output_name, "w", encoding="utf8") as output_file:
            output_file.write(contents)

        # add terms to search index
        if config.index:
            update_search_index(contents, title)


###

def update_search_index(contents, title):
    """Update the search index with strings extracted from metadata for a Markdown file.
    If the file's metadata contains the key 'noindex' with the value 'true' then the
    file will not be indexed.

    Args:
        contents (str): the contents of a Markdown file
        title (str): title of the document

    Returns:
        None
    """

    # test for 'noindex' metadata
    noindex = parse_metadata('noindex', contents)

    if noindex == 'true':
        return

    # at this point must have a title
    terms = parse_metadata("title", contents)

    alias = parse_metadata("alias", contents)

    if alias:
        terms += " " + alias

    summary = parse_metadata("summary", contents)

    if summary:
        terms += " " + summary

    tags = parse_metadata("tags", contents)

    if tags:
        # convert tags list to string
        terms += " " + " ".join(tags)

    keywords = parse_metadata("keywords", contents)

    if keywords:
        # convert keywords list to string
        terms += " " + " ".join(keywords)

    # remove punctuation etc from YAML values, make lower case, remove commas (e.g. from numbers in summary)
    table = str.maketrans(";_()", "    ")
    terms = terms.translate(table).replace(",", "").lower().split()

    # remove stop words
    terms = [word for word in terms if word not in stop_list]

    if config.invert:
        for term in list(set(terms)):
            if term in page_index['search']:
                # append/extend file and title to existing
                page_index['search'][term].append((page_index['title'][title], title))
            else:
                page_index['search'][term] = []
                page_index['search'][term].append((page_index['title'][title], title))
    else:
        # update search index, use unique terms only (set() removes duplicates)
        search = {"file": page_index["title"][title],
                  "title": title,
                  "terms": list(set(terms))}

        page_index["search"].append(search)


###

# TODO make these private?
# TODO put the config stuff as optional args, so don't need global config object?

def convert_page_link(page):
    """Convert a page title into an intra-page link

    Args:
        page (str): The intra-page link in 'mokuwiki' markup. Typically this
        will be `[[Page name]]` or `[[Show name|Page name]]` or with namespaces
        `[[ns:Page name]]` or `[[Show name|ns:Page name]]`

    Returns:
        str: Markdown formatted link to a page

    """

    page_name = str(page.group())[2:-2]
    show_name = ""

    if "|" in page_name:
        show_name, page_name = page_name.split("|")

    # resolve namespace
    namespace = ""

    if ":" in page_name:
        namespace, page_name = page_name.rsplit(":", 1)

        namespace = namespace.replace(":", os.sep) + os.sep

        if not config.fullns:
            # usually assume sibling namespaces
            namespace = os.pardir + os.sep + namespace

    # set show name if not already done
    if not show_name:
        show_name = page_name

    # resolve any alias for the title
    if page_name in page_index["alias"]:
        page_name = page_index["alias"][page_name]

    page_link = ""

    if page_name in page_index["title"]:
        # if title exists in index make into a link
        # page_link = "[" + show_name + "](" + page_index["title"][page_name] + ".html)"
        page_link = f"[{show_name}]({page_index['title'][page_name]}.html)"

    else:
        if namespace:
            # title not in index but namespace set, make up link on the fly
            #page_link = "[" + show_name + "](" + namespace + create_valid_filename(page_name) + ".html)"
            page_link = f"[{show_name}]({namespace}{create_valid_filename(page_name)}.html)"
        else:
            # if title does not exist in index then turn into bracketed span with class='broken' (default)
            #page_link = "[" + page_name + "]{." + config.broken + "}"
            page_link = f"[{page_name}]{{.{config.broken}}}"

            page_index["broken"].add(page_name)

    return page_link


###

def convert_tags_link(tags):
    """Convert a tag specification into a string containing 'mokuwiki' intra-page links

    Args:
        tags (list): list of strings containing a tag specification

    Returns:
        str: A string containing the intra-page links corresponding to the tag
        specification

        Note that the string contains the 'mokuwiki' markup for intra-page links with each link
        separated by two '\n' characters.

    """

    tag_list = str(tags.group())[2:-2]
    tag_list = tag_list.split()

    # get initial category
    tag_name = tag_list[0].replace("_", " ").lower()
    tag_links = ""

    # check that first tag value exists
    if tag_name not in page_index["tags"]:

        # check for special characters
        if "*" in tag_name:
            # if the first tag contains a "*" then list all pages
            # tag_links = "[[" + "]]\n\n[[".join(sorted(page_index["title"].keys())) + "]]\n\n"
            tag_links = "]]\n\n[[".join(sorted(page_index["title"].keys()))
            tag_links = f"[[{tag_links}]]"

        elif "@" in tag_name:
            # if the first tag contains a "@" then list all tags as bracketed span with class='tag' (default)
            # tag_class = "]{." + config.tag + "}\n\n["
            tag_class = f"]{{.{config.tag}}}\n\n["
            # tag_links = "[" + tag_class.join(sorted(page_index["tags"].keys())) + "]{." + config.tag + "}"
            tag_links = tag_class.join(sorted(page_index["tags"].keys()))
            tag_links = f"[{tag_links}]{{.{config.tag}}}"

        elif "#" in tag_name:
            # if the first tag contains a "#" then return the count of pages

            if tag_name == "#":
                # a single "#" returns total number of pages
                tag_links = str(len(list(page_index["title"].keys())))
            else:
                # the string "#tag" returns number of pages with that tag
                if tag_name[1:] in page_index["tags"]:
                    tag_links = str(len(page_index["tags"][tag_name[1:]]))

    else:
        # copy first tag set
        page_set = set(page_index["tags"][tag_name])

        # add other categories
        for __, tag in enumerate(tag_list[1:]):

            if tag[0] == '+' or tag[0] == '-':
                tag_name = tag[1:]
            else:
                tag_name = tag

            # normalise tag name
            tag_name = tag_name.replace("_", " ").lower()

            if tag_name not in page_index["tags"]:
                continue

            if tag[0] == '+':
                page_set &= page_index["tags"][tag_name]
            elif tag[0] == '-':
                page_set -= page_index["tags"][tag_name]
            else:
                page_set |= page_index["tags"][tag_name]

        # format the set into a string of page links, sorted alphabetically
        # tag_links = "[[" + "]]\n\n[[".join(sorted(page_set)) + "]]\n\n"
        tag_links = "]]\n\n[[".join(sorted(page_set))
        tag_links = f"[[{tag_links}]]\n\n"

    # return list of tag links
    return tag_links


###

def convert_file_link(file):
    """Return the contents of a file

    Args:
        file (str): the file path

    Returns:
        str: the contents of the file path, with any YAML metadata blocks removed

    """
    # insert contents of file

    incl_file = str(file.group())[2:-2]

    file_sep = ''
    line_prefix = ''
    options = ''

    # get file separator, if any
    if '|' in incl_file:
        incl_file, *options = incl_file.split('|')

    if len(options) == 1:
        file_sep = options[0]

    if len(options) == 2:
        file_sep = options[0]
        line_prefix = options[1]

    # create list of files
    incl_list = sorted(glob.glob(os.path.normpath(os.path.join(os.getcwd(), incl_file))))

    incl_contents = ''

    for i, file in enumerate(incl_list):

        with open(file, "r", encoding="utf8") as input_file:
            file_contents = input_file.read()

        # TODO check contents for file include regex to do nested includes?

        # remove any YAML block
        file_contents = regex_meta["yaml"].sub("", file_contents)

        # add prefix if required
        if line_prefix:
            file_contents = line_prefix + re.sub('\n', '\n' + line_prefix, file_contents)

        if i < len(incl_list) - 1:
            file_contents += "\n\n" + file_sep

        incl_contents += file_contents + "\n\n"

    # return contents of all matched files
    return incl_contents


###

def convert_image_link(image):
    # return a string containing an image link

    image_name = str(image.group())[2:-2]

    file_ext = "jpg"

    if "|" in image_name:
        image_name, file_ext = image_name.split("|")

    # image_link = "![" + image_name + "](" + os.path.join(config.media, create_valid_filename(image_name)) + "." + file_ext + ")"

    image_link = f"![{image_name}]({os.path.join(config.media, create_valid_filename(image_name))}.{file_ext})"

    return image_link


###

def convert_exec_link(command):
    """Return the output of a shell command as a string

    """
    # return a string containing results of a command

    cmd_name = str(command.group())[2:-2]

    cmd_name = shlex.split(cmd_name)

    # if last element of cmd_name contains * or ? then glob it and the result back to the cmd_name list
    if any(c in "*?" for c in cmd_name[-1]):
        cmd_name = cmd_name[:-1] + sorted(glob.glob(os.path.normpath(os.path.join(os.getcwd(), cmd_name[-1]))))

    cmd_output = subprocess.run(cmd_name, stdout=subprocess.PIPE, shell=False, universal_newlines=True, encoding='utf-8')

    return str(cmd_output.stdout)


###

def create_valid_filename(name):
    """Return a valid filename from a string

    See https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename

    """
    # return a valid filename from the given name

    # see also https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename and Django comment about removing unicode chars
    name = str(name).strip().replace(' ', '_').lower()
    return re.sub(r'(?u)[^-\w.]', '', name)


###

def parse_metadata(metadata, contents):
    # return the contents for the given metadata string, using the global regex's
    # return type is string for simple fields, list for lists

    if metadata not in regex_meta:
        return None

    value = regex_meta[metadata].search(contents)

    if not value:
        return None

    # get raw string value
    value = value.group(1).strip()

    # convert to list if required
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1].split(",")

    return value


###

def reset_page_index():
    global page_index
    page_index = {}
    page_index['tags'] = {}        # index of tags, with set of titles with that tag
    page_index['title'] = {}       # index of titles, with associated base file name
    page_index['alias'] = {}       # index of title aliases
    if config.invert:
        page_index['search'] = {}  # index of search terms (for inverted JSON search index)
    else:
        page_index['search'] = []  # index of search terms (for JSON search index)
    page_index['broken'] = set()   # index of broken links (page names not in index)


### MAIN ###

__version__ = '1.0.0'

# regular expressions to locate YAML metadata

regex_meta = {}
regex_meta["title"] = re.compile(r"title:(.*)[\r\n|\r|\n]", re.IGNORECASE)
regex_meta["alias"] = re.compile(r"alias:(.*)[\r\n|\r|\n]", re.IGNORECASE)
regex_meta["tags"] = re.compile(r"tags:(.*)[\r\n|\r|\n]", re.IGNORECASE)
regex_meta["keywords"] = re.compile(r"keywords:(.*)[\r\n|\r|\n]", re.IGNORECASE)
regex_meta["summary"] = re.compile(r"summary:(.*)[\r\n|\r|\n]", re.IGNORECASE)
regex_meta["noindex"] = re.compile(r"noindex:(.*)[\r\n|\r|\n]", re.IGNORECASE)
regex_meta["yaml"] = re.compile(r"---[\r\n|\r|\n].*[\r\n|\r|\n]\.\.\.", re.DOTALL)

# regular expressions to locate page, tag, file and image links

regex_link = {}
regex_link["page"] = re.compile(r"\[\[[\w\s,.:|'-]*\]\]")
regex_link["tags"] = re.compile(r"\{\{[\w\s\*#@'+-]*\}\}")
regex_link["file"] = re.compile(r"<<[\w\s,./:|'*?\>-]*>>")
regex_link["image"] = re.compile(r"!![\w\s,.:|'-]*!!")
regex_link["exec"] = re.compile(r"%%.*%%")  # TODO disallow redirects?

# page index

page_index = {}

# list of stop words for search indexing

stop_list = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'if', 'i', 'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on', 'or', 'such', 'that', 'the', 'their', 'then', 'there', 'these', 'they', 'this', 'to', 'was', 'will', 'with']

# configuration object


class Config(object):
    pass


config = Config()

# set defaults

config.single = False
config.index = False
config.report = False
config.fullns = False
config.invert = True
config.prefix = 'var MW = MW || {};\nMW.searchIndex = '
config.broken = "broken"
config.tag = "tag"
config.media = "images"

# execute if main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert folder of Markdown files to support interpage linking and tags")
    parser.add_argument("source", help="Source directory")
    parser.add_argument("target", help="Target directory")
    parser.add_argument("-s", "--single", help="Single file mode", action="store_true")
    parser.add_argument("-i", "--index", help="Produce JSON search index", action="store_true")
    parser.add_argument("-v", "--invert", help="Produce JSON search index", action="store_true")
    parser.add_argument("-p", "--prefix", help="Prefix for JSON search index", action="store")
    parser.add_argument("-r", "--report", help="Report broken links", action="store_true")
    parser.add_argument("-f", "--fullns", help="Use full paths for namespaces", action="store_true")
    parser.add_argument("-b", "--broken", default="broken", help="CSS class for broken links (default: 'broken')")
    parser.add_argument("-t", "--tag", default="tag", help="CSS class for tag links (default: 'tag')")
    parser.add_argument("-m", "--media", default="images", help="Path to media files (default:  'images')")
    parser.parse_args(namespace=config)

    mokuwiki(config.source, config.target,
            single=config.single, index=config.index, invert=config.invert, report=config.report,
            fullns=config.fullns, prefix=config.prefix, broken=config.broken, tag=config.tag,
            media=config.media)
