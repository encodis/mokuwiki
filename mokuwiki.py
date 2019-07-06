"""mokuwiki.py

Process a source folder of Markdown files, applying certain directives and
outputting converted files to a target folder. These target files can then be
processed using a regular Markdown processor (*pandoc* is assumed). YAML
metadata fields in the source files control determine the target file name
and how directives are resolved.

Directives include:

-   Link to another page in the same folder: `[[Page Two]]`,
or `[[2nd Page|Page Two]]`
-   List pages with a tag (or combination of tags): `{{tag1}}`,
`{{tag1 +tag2}}` etc
-   Include the contents of another file: `<<include_file.md>>`,
or `<<include_file*.md>>`
-   Link to an image in a standard folder: `!!Image Name!!`
-   Include the output of an external command in the file:
`%% ls -l test/*.md %%`
-   Exclude lines from the corresponding target file by using comment
syntax: `//A comment`

"""

import os
import sys
import re
import json
import glob
import argparse
import subprocess
import shlex
import yaml

# version
__version__ = '1.0.0'

# global page index
page_index = {}

# global configuration
config = {}


def mokuwiki(source, target,
             verbose=False, single=False, index=False, report=False, fullns=False,
             noise='', prefix='', fields='title,alias,tags,summary,keywords',
             broken='broken', tag='tag', media='images'):

    # configure global config object
    config['source'] = source
    config['target'] = target
    config['verbose'] = verbose
    config['single'] = single
    config['index'] = index
    config['report'] = report
    config['fullns'] = fullns
    config['noise'] = noise
    config['prefix'] = prefix
    config['fields'] = fields.split(',')
    config['broken'] = broken
    config['tag'] = tag
    config['media'] = media

    # default file spec
    file_spec = '*.md'

    # check source folder
    if not os.path.isdir(config['source']):
        # not a dir, so first assume a file spec also given
        config['source'], file_spec = config['source'].rsplit(os.sep, 1)

        # CHECK do we really want a filespec allowed outside of single file mode?
        # now check again
        if not os.path.isdir(config['source']):
            print(f"mokuwiki: source folder '{config['source']}' does not exist or is not a folder")
            exit()

    # get list of input files
    file_list = glob.glob(os.path.normpath(os.path.join(config['source'], file_spec)))

    # check single file mode configuration
    if config['single']:
        # cannot generate search index in single file mode
        config['index'] = False

        if len(file_list) > 1:
            print("mokuwiki: single file mode specified but more than one input file found")
            exit()
    else:
        if not os.path.isdir(config['target']):
            print(f"mokuwiki: target folder '{config['target']}' does not exist or is not a folder")
            exit()

    # load noise word file if required
    # TODO should be function
    if config['noise']:
        try:
            with open(config['noise'], 'r', encoding='utf8') as noise_file:
                noise_words = noise_file.read()
            config['noise'] = noise_words.split('\n')
        except IOError:
            print(f"mokuwiki: could not open noise file '{config['noise']}' ")
    else:
        config['noise'] = default_noise_words()

    # first pass - create indexes, update file list
    file_list = create_indexes(file_list)

    # second pass - process files
    process_files(file_list)

    # show list of broken links
    if config['report']:
        print('\n'.join(sorted(page_index['broken'])))

    # write out search index (unless in single file mode)
    if config['index']:
        search_index = config['prefix'] + json.dumps(page_index['search'], indent=2)

        with open(os.path.join(config['target'], "_index.json"), "w", encoding="utf8") as json_file:
            json_file.write(search_index)


def create_indexes(file_list):
    """Create all relevant indexes by scanning each file in the given file list.
    Returns a list of files with duplicates removed (for subsequent processing);
    if this is not done then files with duplicate titles will overwrite existing
    ones on output processing.

    Args:
        file_list (list): list of files to be indexed

    Returns:
        list: list of files with duplicate titles removed

    """

    # reset page indexes
    reset_page_index()

    skip_list = []

    # create all indexes
    for file in file_list:

        if config['verbose']:
            print(f"mokuwiki: indexing '{file}'...")

        try:
            with open(file, 'r', encoding='utf8') as input_file:
                contents = input_file.read()
        except IOError:
            print(f"mokuwiki: could not read '{file}'")
            continue

        # get YAML metadata
        metadata, _ = split_doc(contents)

        if not metadata:
            print(f"mokuwiki: skipping '{file}', no metadata")
            continue

        if 'title' not in metadata:
            print(f"mokuwiki: skipping '{file}', no title in metadata")
            continue

        title = metadata['title']

        if title not in page_index['title']:
            page_index['title'][title] = create_valid_filename(title)
        else:
            print(f"mokuwiki: skipping '{file}', duplicate title '{title}'")
            skip_list.append(file)
            continue

        # get alias (if any)
        if 'alias' in metadata:
            alias = metadata['alias']

            if alias not in page_index['alias'] and alias not in page_index['title']:
                page_index['alias'][alias] = title
            else:
                print(f"mokuwiki: duplicate alias '{alias}', in file '{file}'")

        # get list of tags (if any)
        if 'tags' in metadata:
            tags = metadata['tags']

            # strip end spaces and convert to lower case
            tags = [tag.strip().lower() for tag in tags]

            # add each tag to index, with titles as set
            for tag in tags:
                if tag not in page_index['tags']:
                    page_index['tags'][tag] = set()

                page_index['tags'][tag].add(title)

    # remove files that were skipped and return new list
    return [file for file in file_list if file not in skip_list]


def process_files(file_list):
    """Read and process all files, implementing all directives contained in the
    file and writing out the target file. Assumes that 'file_list' has had files
    with duplicate titles removed.

    Args:
        file_list (list): list of files to be processed

    Returns:
        None

    """

    # compile regular expressions to identify directives
    directive_page = re.compile(r"\[\[[\w\s,.:|'-]*\]\]")
    directive_tags = re.compile(r"\{\{[\w\s\*#@'+-]*\}\}")
    directive_file = re.compile(r"<<[\w\s,./:|'*?\>-]*>>")
    directive_image = re.compile(r"!![\w\s,.:|'-]*!!")
    directive_exec = re.compile(r"%%.*%%")
    directive_comment = re.compile(r"\/\/.*$", re.MULTILINE)

    # process each file in list
    for file in file_list:

        if config['verbose']:
            print(f"processing '{file}'...")

        try:
            with open(file, 'r', encoding='utf8') as input_file:
                contents = input_file.read()
        except IOError:
            print(f"mokuwiki: could not read '{file}'")
            continue

        # get YAML metadata
        metadata, _ = split_doc(contents)

        if not metadata:
            print(f"mokuwiki: skipping '{file}', no metadata")
            continue

        if 'title' not in metadata:
            print(f"mokuwiki: skipping '{file}', no title in metadata")
            continue

        title = metadata['title']

        if title not in page_index['title']:
            print(f"mokuwiki: skipping '{file}', duplicate title '{title}'")
            continue

        # remove comments
        contents = directive_comment.sub('', contents)

        # add terms to search index (after comments removed but before other directives, in case _body_ is an index field)
        if config['index']:
            update_search_index(contents, title)

        # replace file transclusion first (may include tag and page links)
        contents = directive_file.sub(convert_file_link, contents)

        # replace exec links next
        contents = directive_exec.sub(convert_exec_link, contents)

        # replace tag links next (this may create page links, so do this before page links)
        contents = directive_tags.sub(convert_tags_link, contents)

        # replace page links
        contents = directive_page.sub(convert_page_link, contents)

        # replace image links
        contents = directive_image.sub(convert_image_link, contents)

        # get output file name by adding ".md" to title's file name
        if config['single']:
            output_name = config['target']
        else:
            output_name = os.path.join(config['target'], page_index['title'][title] + '.md')

        try:
            with open(output_name, 'w', encoding='utf8') as output_file:
                output_file.write(contents)
        except IOError:
            print(f"mokuwiki: could not write '{file}'")


def update_search_index(contents, title):
    """Update the search index with strings extracted from metadata in a
    Markdown file. If the file's metadata contains the key 'noindex' with the
    value 'true' then the file will not be indexed.

    Args:
        contents (str): the entire contents of the Markdown file, including metadata
        title (str): the title of the document

    Returns:
        None

    """

    if config['verbose']:
        print(f"updating index for title '{title}'...")

    # get YAML metadata
    metadata, body = split_doc(contents)

    if not metadata:
        print(f"mokuwiki: skipping index update for '{title}', no metadata")
        return

    # test for 'noindex' metadata
    if 'noindex' in metadata and metadata['noindex']:
        return

    terms = ''

    for field in config['fields']:
        if field == '_body_':
            terms += ' ' + body
        elif field in metadata and metadata[field]:
            if type(metadata[field]) is str:
                terms += ' ' + metadata[field]
            elif type(metadata[field]) is list:
                # if field is a list, convert to string before adding
                terms += ' ' + ' '.join(metadata[field])
            else:
                print(f"mokuwiki: unknown metadata type '{field}' in page title: '{title}'")
        else:
            pass

    # remove punctuation etc from YAML values, make lower case
    terms = re.sub('[^a-zA-Z0-9 ]', '', terms.lower())

    # remove noise words
    terms = [term for term in terms.split() if term not in config['noise']]

    # update index of unique terms
    for term in list(set(terms)):
        if term not in page_index['search']:
            page_index['search'][term] = []

        page_index['search'][term].append((page_index['title'][title], title))


def convert_page_link(page):
    """Convert a page title in double square brackets into an inter-page link.
    Typically this will be `[[Page name]]` or `[[Display name|Page name]]`, or
    with namespaces `[[ns:Page name]]` or `[[Display name|ns:Page name]]`.

    Args:
        page (Match): A Match object corresponding to an inter-page link

    Returns:
        str: Markdown formatted link to a page,
        e.g. `[Page name](./page_name.html)`

    """

    page_name = str(page.group())[2:-2]
    show_name = ''

    if '|' in page_name:
        show_name, page_name = page_name.split('|')

    # resolve namespace
    namespace = ''

    if ':' in page_name:
        namespace, page_name = page_name.rsplit(':', 1)

        namespace = namespace.replace(':', os.sep) + os.sep

        if not config['fullns']:
            # usually assume sibling namespaces
            namespace = os.pardir + os.sep + namespace

    # set show name if not already done
    if not show_name:
        show_name = page_name

    # resolve any alias for the title
    if page_name in page_index['alias']:
        page_name = page_index['alias'][page_name]

    if page_name in page_index['title']:
        # if title exists in index make into a link
        page_link = f"[{show_name}]({page_index['title'][page_name]}.html)"

    else:
        if namespace:
            # title not in index but namespace set, make up link on the fly
            page_link = f"[{show_name}]({namespace}{create_valid_filename(page_name)}.html)"
        else:
            # if title does not exist in index then turn into bracketed span with class='broken' (default)
            page_link = f"[{page_name}]{{.{config['broken']}}}"

            page_index['broken'].add(page_name)

    return page_link


def convert_tags_link(tags):
    """Convert a tag specification into a string containing inter-page links to
    pages marked with those tags.

    Args:
        tags (Match): A match object corresponding to a tag specification

    Returns:
        str: Markdown formatted link to page(s) whose tag match the
        specification

        Note that each link is separated by a blank line.

    """

    tag_list = str(tags.group())[2:-2]
    tag_list = tag_list.split()

    # get initial category
    tag_name = tag_list[0].replace('_', ' ').lower()
    tag_links = ''

    # check that first tag value exists
    if tag_name not in page_index['tags']:

        # check for special characters
        if '*' in tag_name:
            # if the first tag contains a "*" then list all pages
            tag_links = ']]\n\n[['.join(sorted(page_index['title'].keys()))
            tag_links = f'[[{tag_links}]]'

        elif '@' in tag_name:
            # if the first tag contains a "@" then list all tags as bracketed span with class='tag' (default)
            tag_class = f"]{{.{config['tag']}}}\n\n["
            tag_links = tag_class.join(sorted(page_index['tags'].keys()))
            tag_links = f"[{tag_links}]{{.{config['tag']}}}"

        elif '#' in tag_name:
            # if the first tag contains a "#" then return the count of pages

            if tag_name == '#':
                # a single "#" returns total number of pages
                tag_links = str(len(list(page_index['title'].keys())))
            else:
                # the string "#tag" returns number of pages with that tag
                if tag_name[1:] in page_index['tags']:
                    tag_links = str(len(page_index['tags'][tag_name[1:]]))

    else:
        # copy first tag set
        page_set = set(page_index['tags'][tag_name])

        # add other categories
        for __, tag in enumerate(tag_list[1:]):

            if tag[0] == '+' or tag[0] == '-':
                tag_name = tag[1:]
            else:
                tag_name = tag

            # normalise tag name
            tag_name = tag_name.replace('_', ' ').lower()

            if tag_name not in page_index['tags']:
                continue

            if tag[0] == '+':
                page_set &= page_index['tags'][tag_name]
            elif tag[0] == '-':
                page_set -= page_index['tags'][tag_name]
            else:
                page_set |= page_index['tags'][tag_name]

        # format the set into a string of page links, sorted alphabetically
        tag_links = ']]\n\n[['.join(sorted(page_set))
        tag_links = f'[[{tag_links}]]\n\n'

    # return list of tag links
    return tag_links


def convert_file_link(file):
    """Reads the content of all files matching the file specification (removing
    YAML metadata blocks is required) for insertion into the calling file.
    Optionally add a separator between each file and/or add a prefix to each
    line of the included files.

    Args:
        file (Match): A Match object corresponding to the file specification

    Returns:
        str: the concatentated contents of the file specification

    """

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

        with open(file, 'r', encoding='utf8') as input_file:
            file_contents = input_file.read()

        # TODO check contents for file include regex to do nested includes?

        # remove YAML header from file
        _, file_contents = split_doc(file_contents)

        if not file_contents:
            continue

        # add prefix if required
        if line_prefix:
            file_contents = line_prefix + re.sub('\n', '\n' + line_prefix, file_contents)

        if i < len(incl_list) - 1:
            file_contents += '\n\n' + file_sep

        incl_contents += file_contents + '\n\n'

    # return contents of all matched files
    return incl_contents


def convert_image_link(image):
    """Convert an image linke specification into a Markdown image link

    Args:
        image (Match): A Match object corresponding to an image link

    Returns:
        str: Markdown formatted link to the image

    """

    image_name = str(image.group())[2:-2]

    file_ext = 'jpg'

    if '|' in image_name:
        image_name, file_ext = image_name.split('|')

    image_link = f"![{image_name}]({os.path.join(config['media'], create_valid_filename(image_name))}.{file_ext})"

    return image_link


def convert_exec_link(command):
    """Execute a shell command and return the output as a string for inclusion
    into another file.

    Args:
        command (Match): A Match object corresponding to a shell command

    Returns:
        str: the output of the command

    """

    cmd_name = str(command.group())[2:-2]

    cmd_name = shlex.split(cmd_name)

    # if last element of cmd_name contains * or ? then glob it and the result back to the cmd_name list
    if any(c in '*?' for c in cmd_name[-1]):
        cmd_name = cmd_name[:-1] + sorted(glob.glob(os.path.normpath(os.path.join(os.getcwd(), cmd_name[-1]))))

    cmd_output = subprocess.run(cmd_name, stdout=subprocess.PIPE, shell=False, universal_newlines=True, encoding='utf-8')

    return str(cmd_output.stdout)


def create_valid_filename(name):
    """Return a valid filename from a string. See
    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    for what 'valid' means in this context


    Args:
        name (str): A name (usually a page or image title)

    Returns:
        str: A valid string

    """

    name = str(name).strip().replace(' ', '_').lower()
    return re.sub(r'(?u)[^-\w.]', '', name)


def split_doc(content):
    """Split a document contents into the YAML metadata and the content
    itself.

    Args:
        contents (str): A string starting with a YAML block (delimited
        by '---' and '...')

    Returns:
        dict, str: A tuple consisting of the metadata (as a dictionary)
        and the body of the content.

    """

    # NOTE: python-frontmatter insists on ending metadata with ---
    match = re.match(r'(^---.*?\.\.\.)?(.*)', content, flags=re.DOTALL)

    if match:
        # check for "plain text" file, i.e. no header
        match = match.groups()

        if match[0] is None:
            return None, match[1]
        else:
            return yaml.safe_load(match[0]), match[1]
    else:
        return None, None


def reset_page_index():
    """Reset the global index of pages, tags etc.

    Args:
        None

    Returns:
        None

    """

    global page_index
    page_index = {}

    page_index['title'] = {}       # index of titles, with associated base file name
    page_index['alias'] = {}       # index of title aliases
    page_index['tags'] = {}        # index of tags, with set of titles with that tag
    page_index['broken'] = set()   # index of broken links (page names not in index)
    page_index['search'] = {}      # index of search terms (for inverted JSON search index)


def default_noise_words():
    return ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for',
            'if', 'i', 'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on',
            'or', 'such', 'that', 'the', 'their', 'then', 'there', 'these',
            'they', 'this', 'to', 'was', 'will', 'with']


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Convert folder of Markdown files to support interpage linking and tags')

    parser.add_argument('source', help='Source directory')
    parser.add_argument('target', help='Target directory')
    parser.add_argument('-v', '--verbose', help='Output current file and task', action='store_true', default=False)
    parser.add_argument('-s', '--single', help='Run in single file mode', action='store_true', default=False)
    parser.add_argument('-i', '--index', help='Produce a search index (JSON)', action='store_true', default=False)
    parser.add_argument('-p', '--prefix', help='Prefix string for search index', action='store', default='')
    parser.add_argument('-f', '--fields', help='Metadata fields to search for index', action='store', default='title,alias,tags,summary,keywords')
    parser.add_argument('-n', '--noise', help='File of noise words to remove from search index', action='store', default='')
    parser.add_argument('-r', '--report', help='Report broken links', action='store_true', default=False)
    parser.add_argument('-F', '--fullns', help='Use full paths for namespaces', action='store_true', default=False)
    parser.add_argument('-b', '--broken', help='CSS class for broken links', default='broken')
    parser.add_argument('-t', '--tag', help='CSS class for tag links', default='tag')
    parser.add_argument('-m', '--media', help='Path to media files', default='images')

    config = vars(parser.parse_args(args))

    # TODO ensure that fields is not empty if index=True

    mokuwiki(config['source'],
             config['target'],
             verbose=config['verbose'],
             single=config['single'],
             index=config['index'],
             report=config['report'],
             fullns=config['fullns'],
             noise=config['noise'],
             prefix=config['prefix'],
             fields=config['fields'],
             broken=config['broken'],
             tag=config['tag'],
             media=config['media'])


# execute if main
if __name__ == '__main__':
    main()
