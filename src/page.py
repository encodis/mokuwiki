"""Page class
"""

import os
import re
import sys
import yaml
import glob
import argparse
import subprocess

from string import Template


class MetadataReplace(Template):
    delimiter = '?'


class Page():

    comment_re = re.compile(r"\/\/\s.*$", re.MULTILINE)
    file_incl_re = re.compile(r"<<([\w\s,./:|'*?\>-]*)>>")
    exec_cmd_re = re.compile(r"%%(.*)%%")
    tags_repl_re = re.compile(r"\{\{([\w\s\*#@'+-]*)\}\}")
    page_link_re = re.compile(r"\[\[([\w\s,.:|'-]*)\]\]")
    image_link_re = re.compile(r"!!([\w\s,.:|'-]*)!!")
    custom_style_re = re.compile(r"\^\^([a-zA-Z()\s\d.,_+\[\]-]*?)\^\^")

    def __init__(self, page_file, namespace):
        """Page initialization

        Args:
            file (FileType): input file path
        """

        # file name might be empty
        if not page_file:
            self.valid = False
            return

        # read file
        try:
            with open(page_file, 'r', encoding='utf8') as f:
                contents = f.read()
        except IOError:
            # maybe 'file' was actually a string? try reading directly
            contents = page_file

        if '...' in contents:
            self.meta, _, self.body = contents.partition('...\n')
        else:
            print(f'Incorrect metadata specification in {page_file}')
            self.valid = False
            return

        try:
            self.meta = yaml.safe_load(self.meta)
        except yaml.YAMLError:
            print(f'Error in metadata for {page_file}')
            self.valid = False
            return

        self.file = page_file

        self.namespace = namespace

        self.wiki = self.namespace.wiki if self.namespace else None

        self.modified = os.path.getmtime(page_file)

        self.valid = True

    def __str__(self):
        return '---' + yaml.safe_dump(self.meta, default_flow_style=None) + '...' + self.body

    @property
    def title(self):
        return self.meta['title'] if 'title' in self.meta else ''

    @property
    def alias(self):
        return self.meta['alias'] if 'alias' in self.meta else ''

    @property
    def output(self):
        return create_valid_filename(self.title)

    def save(self, file_name=None):
        # get output file name by adding ".md" to title's file name
        # TODO check wiki and namespace not None
        if not file_name:
            file_name = os.path.join(self.wiki.target, self.namespace.name, self.output) + '.md'

        try:
            with open(file_name, 'w', encoding='utf8') as f:
                f.write(str(self))
        except IOError:
            print(f"mokuwiki: could not write '{file_name}'")

    def process_directives(self):

        # remove comments
        self.body = Page.comment_re.sub('', self.body)

        # not relevant in single file mode
        if self.namespace:
            # process any links in metadata
            self.process_meta_links(self.namespace.wiki.meta_fields)

        # process file includes
        self.body = Page.file_incl_re.sub(self.process_file_includes, self.body)

        # process exec commands
        self.body = Page.exec_cmd_re.sub(self.process_exec_command, self.body)

        # not relevant in single file mode
        if self.namespace:
            # process tag directives
            self.body = Page.tags_repl_re.sub(self.process_tags_directive, self.body)

            # process page links
            self.body = Page.page_link_re.sub(self.process_page_links, self.body)

        # process image links
        self.body = Page.image_link_re.sub(self.process_image_links, self.body)

        # process custom style
        self.body = Page.custom_style_re.sub(self.process_custom_style, self.body)

    def process_meta_links(self, fields):

        # not relevant in single file mode
        if not self.namespace:
            return

        # CHECK any reason we wouldn't do this??
        if not self.namespace.replace:
            return

        # for field in set([fields]).intersection(list(self.meta.keys()))
        for field in fields:
            if field not in self.meta:
                continue

            if isinstance(self.meta[field], list):
                # go through each element of list
                for e in self.meta[field]:
                    self.meta[field][e] = Page.page_link_re.sub(self.process_page_links, self.meta[field][e])
            else:
                # string
                self.meta[field] = Page.page_link_re.sub(self.process_page_links, self.meta[field])

    def process_file_includes(self, path):
        """Reads the content of all files matching the file specification (removing
        YAML metadata blocks if required) for insertion into the calling file.
        Optionally add a separator between each file and/or add a prefix to each
        line of the included files.

        Args:
            file (Match): A Match object corresponding to the file specification

        Returns:
            str: the concatentated contents of the file specification

        """

        incl_file = str(path.group(1))

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

        first_incl = True

        # for i, file in enumerate(incl_list):

        for incl_file in incl_list:
            incl_page = Page(incl_file, self.namespace)

            # TODO check contents for file include regex to do nested includes?

            if not incl_page.valid:
                print(f'Error including file {incl_file}')
                continue

            # add body prefix, suffix
            incl_page.body = incl_page.meta.get('prefix', '') + incl_page.body + incl_page.meta.get('suffix', '')

            if not incl_page.body:
                # nothing to include
                continue

            # replace ?{value}
            # IF no ns, always do this? why would you not do this?
            if self.namespace and self.namespace.replace:
                incl_page.body = MetadataReplace(incl_page.body).safe_substitute(incl_page.meta)

            # add line prefix if required
            if line_prefix:
                incl_page.body = line_prefix + re.sub('\n', '\n' + line_prefix, incl_page.body)

            if first_incl:
                first_incl = False
            else:
                incl_page.body += file_sep + '\n\n'

            # if i < len(incl_list) - 1:
            #     page.body += '\n\n' + file_sep

            incl_contents += incl_page.body + '\n\n'

        # return contents of all matched files
        return incl_contents

    def process_exec_command(self, command):
        """Execute a shell command and return the output as a string for inclusion
        into another file.

        Args:
            command (Match): A Match object corresponding to a shell command

        Returns:
            str: the output of the command

        """

        cmd_args = str(command.group(1))

        cmd_output = subprocess.run(cmd_args, shell=True, capture_output=True, universal_newlines=True, encoding='utf-8')

        return cmd_output.stdout

    def process_tags_directive(self, tags):
        """Convert a tag specification into a string containing inter-page links to
        pages marked with those tags.

        Args:
            tags (Match): A match object corresponding to a tag specification

        Returns:
            str: Markdown formatted link to page(s) whose tag match the
            specification

            Note that each link is separated by a blank line.

        """

        tag_list = str(tags.group(1))
        tag_list = tag_list.split()

        # get initial category
        tag_name = tag_list[0].replace('_', ' ').lower()
        tag_links = ''

        # check that first tag value exists
        if tag_name not in self.namespace.index.tags:

            # check for special characters
            if '*' in tag_name:
                # if the first tag contains a "*" then list all pages
                tag_links = ']]\n\n[['.join(sorted(self.namespace.index.title.keys()))
                tag_links = f'[[{tag_links}]]'

            elif '@' in tag_name:
                # if the first tag contains a "@" then list all tags as bracketed span with class='tag' (default)
                tag_links = f"]{{{self.namespace.wiki.tags_css}}}\n\n["
                tag_links = tag_links.join(sorted(self.namespace.index.tags.keys()))
                tag_links = f"[{tag_links}]{{{self.namespace.wiki.tags_css}}}"

            elif '#' in tag_name:
                # if the first tag contains a "#" then return the count of pages

                if tag_name == '#':
                    # a single "#" returns total number of pages
                    tag_links = str(len(list(self.namespace.index.title.keys())))
                else:
                    # the string "#tag" returns number of pages with that tag
                    if tag_name[1:] in self.namespace.index.tags:
                        tag_links = str(len(self.namespace.index.tags[tag_name[1:]]))

        else:
            # copy first tag set, which must exist
            page_set = set(self.namespace.index.tags[tag_name])

            # add/del/combine other tagged categories
            for tag in tag_list[1:]:

                tag_name = tag[1:] if tag.startswith(('+', '-')) else tag

                # normalise tag name
                tag_name = tag_name.replace('_', ' ').lower()

                if tag[0] == '+':
                    page_set &= self.namespace.index.tags.get(tag_name, set())
                elif tag[0] == '-':
                    page_set -= self.namespace.index.tags.get(tag_name, set())
                else:
                    page_set |= self.namespace.index.tags.get(tag_name, set())

            # format the set into a string of page links, sorted alphabetically
            tag_links = ']]\n\n[['.join(sorted(page_set))
            tag_links = f'[[{tag_links}]]\n\n'

        # return list of tag links
        return tag_links

    def process_page_links(self, page):
        """Convert a page title in double square brackets into an inter-page link.
        Typically this will be `[[Page name]]` or `[[Display name|Page name]]`,
        or with namespaces `[[ns:Page name]]` or `[[Display name|ns:Page name]]`.

        Note: when writing a page link with a namespace must always use the
        alias for that namespace, otherwise it will be flagged as a broken
        link. It is no longer possible to use the 'fullns' option and insert
        a relative path yourself.

        Args:
            page (Match): A Match object corresponding to an inter-page link

        Returns:
            str: Markdown formatted link to a page,
            e.g. `[Page name](./page_name.html)`

        """

        page_name = str(page.group(1))
        show_name = ''

        if '|' in page_name:
            show_name, page_name = page_name.split('|')

        # resolve namespace
        namespace = ''

        if ':' in page_name:
            # e.g. this is a [[x:Page One]] reference
            namespace, page_name = page_name.rsplit(':', 1)

        # set show name if not already done
        if not show_name:
            show_name = page_name

        # resolve namespace aliases
        if namespace:
            target_ns = self.wiki.ns_alias(namespace)

            if target_ns:
                namespace = target_ns.path
        else:
            target_ns = self.namespace

        # resolve any alias for the title in the target index
        if page_name in target_ns.index.alias:
            page_name = target_ns.index.alias[page_name]

        if page_name in target_ns.index.title:
            # if title exists in target namespace index make into a link
            page_link = make_markdown_link(show_name, page_name, namespace)
        else:
            # if title does not exist in index then turn into bracketed span with class='broken' (default)
            page_link = make_markdown_span(page_name, target_ns.wiki.broken_css)
            target_ns.index.broken.add(page_name)

        return page_link

    def process_image_links(self, image):
        """Convert an image link specification into a Markdown image link

        Args:
            image (Match): A Match object corresponding to an image link

        Returns:
            str: Markdown formatted link to the image

        """

        image_name = str(image.group(1))

        file_ext = 'jpg'

        if '|' in image_name:
            image_name, file_ext = image_name.split('|')

        media_dir = self.namespace.media_dir if self.namespace else 'images'

        return make_image_link(image_name, file_ext, media_dir)

    def process_custom_style(self, style):
        """Convert a custom style specification into a (Pandoc) bracketed span

        Args:
            style (Match): A Match object corresponding to a custom style

        Returns:
            str: Pandoc bracketed span

        """

        style_text = str(style.group())[2:-2]

        custom_css = self.namespace.custom_css if self.namespace else '.smallcaps'

        return make_markdown_span(style_text, custom_css)


def create_valid_filename(name, ext=None):
    """Return a valid filename from a string, optionally including a file
    extension. For what 'valid' means in this context, see
    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename

    Args:
        name (str): A name (usually a page or image title)
        ext (str): A file extension (without the dot)

    Returns:
        str: A valid filename

    """

    name = str(name).strip().replace(' ', '_').lower()
    name = re.sub(r'(?u)[^-\w.]', '', name)

    if ext:
        return name + '.' + ext

    return name


def make_markdown_link(show_name, page_name, ns_path=''):
    if ns_path:
        return f'[{show_name}]({os.path.join(os.pardir, ns_path, page_name)}.html)'

    return f'[{show_name}]({page_name}.html)'


def make_image_link(image_name, ext='jpg', media_dir=''):
    if media_dir:
        return f'![{image_name}]({os.path.join(media_dir, create_valid_filename(image_name, ext))})'

    return f'![{image_name}]({create_valid_filename(image_name, ext)})'


def make_markdown_span(page_name, css_class=None):
    if css_class:
        return f'[{page_name}]{{{css_class}}}'
    else:
        return f'[{page_name}]'


def mwpage(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Convert Markdown file with directives')
    parser.add_argument('source', help='Source file')
    parser.add_argument('target', help='Target file')

    # check target is filename and exists (or is folder and exists, add default file name)

    # might need media_dir and custom_css
    # do not need tags_css, broken_css because we cannot process tags and page links in custom mode

    page = Page(args.source, None)
    page.process_directives()
    page.save(args.target)
