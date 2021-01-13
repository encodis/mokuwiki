"""
Page module.

This module contains the definition of the Page class,
as well as a number of useful methods for processing
a page.
"""

import os
import re
import sys
import yaml
import glob
import argparse
import subprocess

from string import Template

import logging
logging.basicConfig(format='mokuwiki: %(levelname)s %(message)s', level=logging.INFO)


class MetadataReplace(Template):
    """Subclass of Template to allow for different
    template character.
    """
    delimiter = '?'


class Page():
    """The Page class definition.

    A Page instance contains the (YAML) metadata and contents of a
    Markdown page. The class definition also includes a number of
    compiled regular expressions as class variables.

    """

    comment_re = re.compile(r"\/\/\s.*$", re.MULTILINE)
    file_incl_re = re.compile(r"<<([\w\s,./:|'*?\>-]*)>>")
    exec_cmd_re = re.compile(r"%%(.*)%%")
    tags_repl_re = re.compile(r"\{\{([\w\s\*#@'+-]*)\}\}")
    page_link_re = re.compile(r"\[\[([\w\s(),.:|'-]*)\]\]")
    image_link_re = re.compile(r"!!([\w\s,.:|'-]*)!!")
    custom_style_re = re.compile(r"\^\^([a-zA-Z()\s\d.,_+\[\]-]*?)\^\^")

    def __init__(self, page_file, namespace, included=False, media='images', custom='.smallcaps'):
        """Initialize a Page object by reading a Markdown file and
        splitting the contents into metadata and body components.

        If, for any reason, the page is deemed to be invalid (e.g. the file
        cannot be opened) then the page will set a 'valid' member attribute to
        'False' and return. This value should be checked before using the page.

        Note: if the namespace is not provided then the page will assume
        that it is being run in "single file mode". Page links and tag
        directives will not be processed.

        Args:
            page_file (str): The page's file name
            namespace (Namespace): The parent namespace of the page.
            included (bool, optional): If true then page was created for an
            include directive and checks are less restrictive. Default is False.
            media (str, optional): When used in "single file mode" used to
            override the media folder name. Defaults to 'images'.
            custom (str, optional): When used in "single file mode"
            used to override the CSS used for the custom style. Defaults to
            '.smallcaps'.
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
            logging.error(f"could not read file '{page_file}'")
            self.valid = False
            return

        if '...' in contents:
            self.meta, _, self.body = contents.partition('...\n')
        else:
            if included:
                # if the file was an include directive and has no YAML marker, then
                # then set meta as empty dict and body to contents of whole file
                self.meta = {}
                self.body = contents
            else:
                logging.warning(f"incorrect metadata specification in '{page_file}'")
                self.valid = False
                return

        if self.meta:
            try:
                self.meta = yaml.safe_load(self.meta)
            except yaml.YAMLError:
                logging.warning(f"error in metadata for '{page_file}'")
                self.valid = False
                return

        self.file = page_file

        self.namespace = namespace

        # mainly for single file mode
        self.media = media
        self.custom = custom

        self.valid = True
        self.modified = os.path.getmtime(page_file)

        logging.debug(f"read page '{self.file}'")

    def __str__(self):
        """The string representation of a page is simply the metadata
        dictionary (as a string) with the contents appended. YAML
        section delimiters are added.

        Returns:
            str: string representation of a page, suitable for writing
            to a file
        """

        return '---\n' + yaml.safe_dump(self.meta, default_flow_style=False) + '...\n' + self.body

    @property
    def title(self):
        return self.meta['title'] if 'title' in self.meta else ''

    @property
    def alias(self):
        return self.meta['alias'] if 'alias' in self.meta else ''

    @property
    def output(self):
        return Page.slugify(self.title)

    @property
    def media_dir(self):
        return self.namespace.media_dir if self.namespace else self.media

    @property
    def custom_css(self):
        return self.namespace.custom_css if self.namespace else self.custom

    def save(self, file_name=None):
        """Save a page to a file. This uses the string representation.

        Args:
            file_name (FileType, optional): A file name to override the
            default one (which is a slugified version of the page title).
            Defaults to None.
        """

        if not file_name:
            target = self.namespace.target if self.namespace else ''
            file_name = os.path.join(target, self.output) + '.md'

        try:
            with open(file_name, 'w', encoding='utf8') as f:
                f.write(str(self))
        except IOError:
            logging.error(f"could not write output file '{file_name}'")

    def process_directives(self):
        """Process the various directives that may be embedded in the page.

        Note: some directives will be skipped if there is no namespace
        defined (i.e. single file mode) as they only make sense with more
        than one page (which implies at least one namespace).

        Note: the directives could be processed during `__init__` but this
        would mean a possible infinite file inclusion issue.
        """

        # remove comments
        self.body = Page.comment_re.sub('', self.body)

        # process file includes
        self.body = Page.file_incl_re.sub(self.process_file_includes, self.body)

        # process exec commands
        self.body = Page.exec_cmd_re.sub(self.process_exec_command, self.body)

        # these directives are not relevant in single file mode (i.e. when namespace == None)
        if self.namespace:
            # process tag directives
            self.body = Page.tags_repl_re.sub(self.process_tags_directive, self.body)

            # process page links
            self.body = Page.page_link_re.sub(self.process_page_directives, self.body)

            # convert metadata into links
            self.convert_metadata_links()

        # process image links
        self.body = Page.image_link_re.sub(self.process_image_links, self.body)

        # process custom style
        self.body = Page.custom_style_re.sub(self.process_custom_style, self.body)

    def convert_metadata_links(self):
        """Convert specified metadata fields into links.

        The (somewhat specialised) use case is as follows: in some
        cases it is useful to convert items in metadata into a page
        link. For example, all 'tags' could be converted into links,
        which assumes there is a page named after each tag. So the tag
        'apple' would be converted into a page link - '[[apple]]' -
        which would then be processed as usual (e.g. into
        '[apple](apple.html)')
        """

        if not self.namespace.meta_fields:
            return

        for field in self.namespace.meta_fields:
            if field not in self.meta:
                continue

            new_fields = []

            if isinstance(self.meta[field], list):
                for item in self.meta[field]:
                    new_field = Page.page_link_re.sub(self.process_page_directives, '[[' + item + ']]')
                    new_fields.append(new_field)

                self.meta[field] = new_fields
            else:
                self.meta[field] = Page.page_link_re.sub(self.process_page_directives, '[[' + self.meta[field] + ']]')

    def process_file_includes(self, path):
        """Reads the content of all files matching the file specification
        (removing YAML metadata blocks if required) for insertion into the
        calling file. Optionally add a separator between each file and/or
        add a prefix to each line of the included files (e.g. to make the
        contents of the included file into a block quote).

        Args:
            file (Match): A Match object corresponding to the file
            specification

        Returns:
            str: the concatentated contents of the file specification
        """

        def get_incl_file_contents(file_name, file_sep='', line_prefix=''):
            """An inner function used when iterating through the list
            of included files. This function was abstracted out to
            make the loop easier to understand. This function also adds
            any prefix and suffix string specified in the metadata.

            Args:
                file_name (FileType): the file name
                file_sep (str, optional): The (Markdown) separator
                to insert between each file. Defaults to ''.
                line_prefix (str, optional): The prefix string to add to
                each line of the file

            Returns:
                str: the file contents of the file, modified by the separator,
                prefix and process options
            """

            incl_page = Page(file_name, self.namespace, included=True)

            # TODO check this is robust against non-existant files
            if not incl_page.valid:
                logging.error(f"error reading file '{file_name}' for inclusion")
                return ''

            # add body prefix, suffix
            incl_page.body = incl_page.meta.get('prefix', '') + incl_page.body + incl_page.meta.get('suffix', '')

            if not incl_page.body:
                # nothing to include
                return ''

            # replace ?{value} strings in content with appropriate metadata values
            incl_page.body = MetadataReplace(incl_page.body).safe_substitute(incl_page.meta)

            # add line prefix if required
            if line_prefix:
                incl_page.body = re.sub('^(.*)', line_prefix + r'\1', incl_page.body, flags=re.MULTILINE)

            return incl_page.body + file_sep

        incl_file = str(path.group(1))

        file_sep = ''
        line_prefix = ''
        process = ''
        options = ''

        # get file separator etc, if any
        if '|' in incl_file:
            incl_file, *options = incl_file.split('|')

        if len(options) == 1:
            file_sep = options[0]

        if len(options) == 2:
            file_sep = options[0]
            line_prefix = options[1]

        if len(options) == 3:
            file_sep = options[0]
            line_prefix = options[1]
            process = options[2]

        # ensure newline separation for Markdown
        if file_sep:
            file_sep = '\n\n' + file_sep + '\n\n'
        else:
            file_sep = '\n\n'

        # resolve namespace ref if present
        if ':' in incl_file:
            # if namespace ref exists list is only one file long
            incl_file = self.namespace.wiki.get_page_path_by_link(incl_file)
            incl_list = [incl_file]
        else:
            # no namespace ref so create globbed list
            incl_list = sorted(glob.glob(os.path.normpath(os.path.join(os.getcwd(), incl_file))))

        # if process is defined run it and return
        if process:
            process_output = subprocess.run(process + ' ' + incl_file, shell=True, capture_output=True, universal_newlines=True, encoding='utf-8')

            return process_output.stdout

        # create list of files
        incl_contents = ''

        if len(incl_list) == 0:
            return incl_contents

        for incl_file in incl_list[:-1]:
            incl_contents += get_incl_file_contents(incl_file, file_sep, line_prefix)
        
        incl_contents += get_incl_file_contents(incl_list[-1], '', line_prefix)

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
        pages marked with those tags. A tag specification is of the form '{{tag}}':

        -  `{{tag}}`: list all pages with 'tag'
        -  `{{tag1 tag2}}`: list all pages with 'tag1' or 'tag2'
        -  `{{tag1 +tag2}}`: list all pages with 'tag1' and 'tag2'
        -  `{{tag1 -tag2}}`: list all pages with 'tag1' but not 'tag2'
        -  `{{*}}`: list all pages in the namespace
        -  `{{@}}`: list all tags as bracketed spans with the CSS class given by
        the 'tag_css' configuration option
        -  `{{#}}`: return the total number of pages in the namespace, as an int
        -  `{{#tag}}`: return the number of pages with 'tag', as an int

        Note that in returned lists each link is separated by a blank line.

        Args:
            tags (Match): A match object corresponding to a tag specification

        Returns:
            str: Markdown formatted link to page(s) whose tag match the
            specification
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
                tag_links = f"]{{{self.namespace.tags_css}}}\n\n["
                tag_links = tag_links.join(sorted(self.namespace.index.tags.keys()))
                tag_links = f"[{tag_links}]{{{self.namespace.tags_css}}}"

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

    def process_page_directives(self, page):
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

        # TODO option to just change links to text rather than mark as broken?

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
            target_ns = self.namespace.wiki.get_ns_by_alias(namespace)

            if not target_ns:
                target_ns = self.namespace.wiki.get_ns_by_name(namespace)

            if not target_ns:
                logging.error(f"no namespace name or alias found for '{namespace}'")
        else:
            target_ns = self.namespace

        # resolve any alias for the title in the target index
        if page_name in target_ns.index.alias:
            page_name = target_ns.index.alias[page_name]

        # TODO really need an API for getting aliases etc

        if page_name in target_ns.index.title:
            # if title exists in target namespace index make into a link
            ns_path = '' if target_ns is self.namespace else target_ns.name
            page_link = Page.make_markdown_link(show_name, target_ns.index.title[page_name], ns_path)
        else:
            # if title does not exist in index then turn into bracketed span with class='broken' (default)
            page_link = Page.make_markdown_span(page_name, target_ns.wiki.broken_css)
            target_ns.index.broken.add(page_name)

        return page_link

    def process_image_links(self, image):
        """Convert an image link specification into a Markdown image link.
        Note that the given image name is 'slugified' and the value of the
        'media_dir' configuration option is prepended to the name.

        For example, `!!An Image!!` becomes `![An Image](images/an_image.png)`

        Args:
            image (Match): A Match object corresponding to an image link

        Returns:
            str: Markdown formatted link to the image

        """

        image_name = str(image.group(1))

        file_ext = 'jpg'

        if '|' in image_name:
            image_name, file_ext = image_name.split('|')

        return Page.make_image_link(image_name, file_ext, self.media_dir)

    def process_custom_style(self, style):
        """Convert a custom style specification into a (Pandoc) bracketed span.
        For example. `^^some text^^` becomes `[some text]{.smallcaps}`.

        Args:
            style (Match): A Match object corresponding to a custom style

        Returns:
            str: Pandoc bracketed span

        """

        style_text = str(style.group())[2:-2]

        return Page.make_markdown_span(style_text, self.custom_css)

    @staticmethod
    def slugify(name, ext=None):
        """Return a valid filename from a string, optionally including a file
        extension. For what 'valid' means in this context, see
        https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename

        Args:
            name (str): A name (usually a page or image title)
            ext (str): A file extension (without the dot). Default is blank.

        Returns:
            str: A valid filename
        """

        name = str(name).strip().replace(' ', '_').lower()
        name = re.sub(r'(?u)[^-\w.]', '', name)

        if ext:
            return name + '.' + ext

        return name

    @staticmethod
    def make_markdown_link(show_name, page_name, ns_path=''):
        # TODO if namespace targets could be different then you would need to
        # factor that in here
        if ns_path:
            return f'[{show_name}]({os.path.join(os.pardir, ns_path, page_name)}.html)'

        return f'[{show_name}]({page_name}.html)'

    @staticmethod
    def make_image_link(image_name, ext='jpg', media_dir=''):
        if media_dir:
            return f'![{image_name}]({os.path.join(media_dir, Page.slugify(image_name, ext))})'

        return f'![{image_name}]({Page.slugify(image_name, ext)})'

    @staticmethod
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
    parser.add_argument('--media', help='Name of media folder', default='images')
    parser.add_argument('--custom', help='String for custom CSS', default='.smallcaps')

    args = parser.parse_args(args)

    page = Page(args.source, None, media=args.media, custom=args.custom)
    page.process_directives()
    page.save(args.target)
