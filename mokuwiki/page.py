import os
import re
from re import Match
import sys
import yaml
import glob
from pathlib import Path
import argparse
import subprocess
from string import Template
from typing import TYPE_CHECKING
from functools import partial

if TYPE_CHECKING:
    from mokuwiki.namespace import Namespace

from mokuwiki.utils import FileIncludeParser, TagListParser
from mokuwiki.utils import make_file_name, make_image_link, make_markdown_link, make_wiki_link, make_markdown_span


import logging
logging.basicConfig(format='mokuwiki: %(levelname)s %(message)s', level=logging.INFO)

MARKDOWN_PARA_SEP = "\n\n"

COMMENT_RE = r"\/\/\s(.*)$"
FILE_INCLUDE_RE = r"<<(.*?)>>"
EXEC_COMMAND_RE = r"%%(.*?)%%"
TAGS_REPLACE_RE = r"\{\{(.*?)\}\}"
PAGE_LINK_RE = r"\[\[(.*?)\]\]"
IMAGE_LINK_RE = r"!!(.*?)!!"
CUSTOM_STYLE_RE = r"\^\^(.*?)\^\^"

MIN_REPEAT_COUNT = 1
MAX_REPEAT_COUNT = 999
MIN_HEADING_LEVEL = 1
MAX_HEADING_LEVEL = 6


class MetadataReplace(Template):
    """Subclass of Template to allow for different template character.
    """
    delimiter = '?'

# TODO page should be able to tell you its rel/abs path and what it's wiki/MD links look like

class Page:
    """The Page class definition.

    A Page instance contains the (YAML) metadata and contents of a
    Markdown page. The class definition also includes a number of
    compiled regular expressions as class variables.

    """

    FileIncludeParser = FileIncludeParser()
    TagListParser = TagListParser()

    def __init__(self, page_path: Path | str, namespace: 'Namespace', included: bool = False, media: str = 'images', custom: str = '.smallcaps') -> None:
        """Initialize a Page object by reading a Markdown file and
        splitting the contents into metadata and body components.

        If, for any reason, the page is deemed to be invalid (e.g. the file
        cannot be opened) then the page will set a 'valid' member attribute to
        'False' and return. This value should be checked before using the page.

        Note: if the namespace is not provided then the page will assume
        that it is being run in "single file mode". Page links and tag
        directives will not be processed.

        Args:
            page_path (Path): The page's file name
            namespace (Namespace): The parent namespace of the page.
            included (bool, optional): If true then page was created for an
            include directive and checks are less restrictive. Default is False.
            media (str, optional): When used in "single file mode" used to
            override the media folder name. Defaults to 'images'.
            custom (str, optional): When used in "single file mode"
            used to override the CSS used for the custom style. Defaults to
            '.smallcaps'.
        """
        # TODO included should really be inc_meta=False or similar
        # file name might be empty
        if not page_path:
            raise ValueError

        # read file
        # TODO should be in self.load(), returns (meta, body)
        try:
            with Path(page_path).open('r', encoding='utf8') as f:
                contents = f.read().strip()
        except IOError:
            logging.error(f"could not read file '{page_path}'")
            raise ValueError
        
        if '...' in contents:
            self.meta, _, self.body = contents.partition('...')
        else:
            if included:
                # if the page is being created as part of an include directive, plain files
                # with missing metadata are allowed
                self.meta = {}
                self.body = contents
            else:
                logging.warning(f"incorrect metadata specification in '{page_path}'")
                raise ValueError

        self.body = self.body.strip()

        if self.meta:
            try:
                self.meta = yaml.safe_load(self.meta)
            except yaml.YAMLError:
                logging.warning(f"error in metadata for '{page_path}'")
                raise ValueError

        try:
            self.target = make_file_name(self.meta['title'])
        except KeyError:
            # included files do not need a target, as they will never be saved
            if included:
                self.target = None
            else:
                raise ValueError(f"page {page_path} has no title")
        
        self.source = page_path        
        self.namespace = namespace

        # remove 'noise' tags for wiki
        # TODO why remove noise tags? also assumes is a list? 
        # TODO this is removing from page not just index?
        if self.namespace:
            if 'tags' in self.meta and self.namespace.config.noise_tags:
                for tag in self.namespace.config.noise_tags:
                    if tag in self.meta['tags']:
                        self.meta['tags'].remove(tag)

        # mainly for single file mode
        # TODO only set if namesapce == none? is that right?
        self._media = media
        self._custom = custom

        self.modified = page_path.stat().st_mtime

        logging.debug(f"created page '{self.source}'")

    def __str__(self) -> str:
        """The string representation of a page is simply the metadata
        dictionary (as a string) with the contents appended. YAML
        section delimiters are added.

        Returns:
            str: string representation of a page, suitable for writing to a file
        """

        # return '\n'.join('---', yaml.safe_dump(self.meta, default_flow_style=False), '...', self.body)

        return '---\n' + yaml.safe_dump(self.meta, default_flow_style=False) + '...\n' + self.body

    @property
    def title(self) -> str:
        # TODO should default be file name? minus extension?
        return self.meta.get('title', '')

    @property
    def alias(self) -> str:
        return self.meta.get('alias', '')

    @property
    def tags(self) -> list[str]:
        return [t.lower() for t in self.meta.get('tags', [])]

    @property
    def toc_level(self) -> int:
        return self.meta.get('toc-level', 1)
    
    @property
    def toc_include(self) -> bool:
        # TODO default should come from namespace...
        return self.meta.get('toc-include', True)

    @property
    def toc_display(self) -> bool:
        return self.meta.get('toc-display', True)
    
    @property
    def toc_order(self) -> int:
        return self.meta.get('toc-order', 99999)
    
    @property
    def noindex(self) -> bool:
        return self.meta.get('noindex', False)

    @property
    def media_dir(self) -> str:
        # for mwpage...
        return self.namespace.config.media_dir if self.namespace else self._media

    @property
    def custom_css(self) -> str:
        # for mwpage...
        return self.namespace.config.custom_css if self.namespace else self._custom

    def content(self, indent: str = '', shift: int = 0) -> str:
        """Fully processed body with prefix, suffix and metadata replacement
        Used really on file includes, not on save (because the pandoc template and other
        code will process prefix/suffix etc)
        
        this does not include metadata block...
        #TODO test for empty body
        
        """
        
        def shift_heading(heading: str, shift: int = 0) -> str:
            
            if not heading.startswith('#'):
                return heading
            
            level, _, text = heading.partition(' ')            
            level = min(MAX_HEADING_LEVEL, max(MIN_HEADING_LEVEL, len(level) + shift))
            
            return f"{'#' * level} {text}"
        
        
        content = self.meta.get('prefix', '') + self.body + self.meta.get('suffix', '')
        
        # replace ?{value} strings in content with appropriate metadata values
        content = MetadataReplace(content).safe_substitute(self.meta)
        
        if shift != 0:
            content = re.sub(r"^(#.*)", lambda h: shift_heading(h.group(), shift), content)
                
        if indent:
            content = re.sub('^(.*)', indent + r'\1', content, flags=re.MULTILINE)

        return content

    def save(self, file_name: str = None) -> None:
        """Save a page to a file. This uses the string representation.

        Args:
            file_name (FileType, optional): A file name to override the
            default one (which is a slugified version of the page title).
            Defaults to None.
        """

        if not self.target:
            # if no target then plain file that was included, cannot save
            logging.error(f"tried to save included file '{self.source}'")
            return

        if not file_name:
            target_dir = self.namespace.config.target_dir if self.namespace else ''
            file_name = Path(target_dir) / self.target
            file_name = file_name.with_suffix('.md')

        try:
            with file_name.open('w', encoding='utf8') as f:
                f.write(str(self))
        except IOError:
            logging.error(f"could not write output file '{file_name}'")

    def process_directives(self) -> None:
        """Process the various directives that may be embedded in the page.

        Note: some directives will be skipped if there is no namespace
        defined (i.e. single file mode) as they only make sense with more
        than one page (which implies at least one namespace).

        Note: the directives could be processed during `__init__` but this
        would mean a possible infinite file inclusion issue.
        """

        # remove comments
        self.body = re.sub(COMMENT_RE, '', self.body, flags=re.MULTILINE)

        # process file includes
        self.body = re.sub(FILE_INCLUDE_RE, self.process_file_includes, self.body)

        # process exec commands
        self.body = re.sub(EXEC_COMMAND_RE, self.process_exec_command, self.body)

        # these directives are not relevant in single file mode (i.e. when namespace == None)
        if self.namespace:
            # process tag directives
            self.body = re.sub(TAGS_REPLACE_RE, self.process_tags_directive, self.body)
            
            # process page links
            self.body = re.sub(PAGE_LINK_RE, self.process_link_directives, self.body)

            # convert metadata into links
            self.convert_metadata_links()

        # process image links
        self.body = re.sub(IMAGE_LINK_RE, self.process_image_links, self.body)

        # process custom style
        self.body = re.sub(CUSTOM_STYLE_RE, self.process_custom_style, self.body)

    def convert_metadata_links(self) -> None:
        """Convert specified metadata fields into links.

        The (somewhat specialised) use case is as follows: in some
        cases it is useful to convert items in metadata into a page
        link. For example, all 'tags' could be converted into links,
        which assumes there is a page named after each tag. So the tag
        'apple' would be converted into a page link - '[[apple]]' -
        which would then be processed as usual (e.g. into
        '[apple](apple.html)')
        """

        process_links = partial(self.process_link_directives, show_broken = self.namespace.config.meta_links_broken)

        if not self.namespace.config.meta_links:
            return

        for field in self.namespace.config.meta_links:
            if field not in self.meta:
                continue

            # TODO next, prev etc are NOT in wiki link format so are not found
            ## if home, next, prev are system type things then we can add
            ## but for subtitle test will have to put directly
            if isinstance(self.meta[field], list):
                self.meta[field] = [re.sub(PAGE_LINK_RE, process_links, f) for f in self.meta[field]]

            if isinstance(self.meta[field], str) and self.meta[field]:
                self.meta[field] = re.sub(PAGE_LINK_RE, process_links, self.meta[field])

    def process_file_includes(self, include: Match) -> str:
        """Reads the content of all files matching the file specification
        (removing YAML metadata blocks if required) for insertion into the
        calling file. Optionally add a separator between each file and/or
        add a prefix to each line of the included files (e.g. to make the
        contents of the included file into a block quote).

        Args:
            file (Match): A Match object corresponding to the file specification
            
            REALL spec or match

        Returns:
            str: the concatenated contents of the file specification
        """
        include = str(include.group(1))
        options = Page.FileIncludeParser.parse(include)

        # replace format. header if in template, else retain
        if options.format:
            options.format = self.namespace.config.templates.get(options.format, options.format)
            
        if options.header:
            options.header = self.namespace.config.templates.get(options.header, options.header)

        # TODO add -pipe option to e.g. include monster and pipe through monster + adhoc 

        page_list = []

        # resolve namespace ref if present
        # TODO replace 'ns1:' with path to content, then glob? this would allow ns1:file*.md?
        if ':' in options.files:
            # if namespace ref exists list is only one file long
            # in DW terms this will be the path in the 'monster' NS
            page = self.namespace.wiki.get_page_by_name(options.files)
            
            if page:
                page_list = [page.source]

        elif '/' in options.files:
            # this is a path spec
            page_list = list(Path('.').glob(options.files))
        
        else:
            # assume this is a file(s) in one of the content_dirs
            for content_dir in self.namespace.config.content_dirs:
                page_list.extend(list(content_dir.glob(options.files)))
                
        # create text
        if len(page_list) == 0:
            return ''

        if len(page_list) == 1 and options.repeat > 1:
            # repeat is only applicable for a single file include
            repeat = min(max(options.repeat, MIN_REPEAT_COUNT), MAX_REPEAT_COUNT)

            page_list = page_list * repeat

        if options.sort:
            # sort by filename
            page_list = sorted(page_list)

        try:
            if options.format:
                # create list of Page objects from paths
                page_list = [Page(p, self.namespace, included=True) for p in page_list]

                incl_text = [MetadataReplace(options.format).safe_substitute(p.meta) for p in page_list]
            else:
                incl_text = [Page(p, self.namespace, included=True).content(options.indent, options.shift) for p in page_list]
        except ValueError:
            # catch Page() errors due to path issues
            logging.warning(f"missing files in include directive '{options.files}'")
            return ''
        
        incl_text = options.sep.join([options.before + 
                                      t +
                                      options.after
                                      for t in incl_text])

        return options.header + incl_text

    def process_exec_command(self, command: Match) -> str:
        """Execute a shell command and return the output as a string for inclusion
        into another file.

        Args:
            command (Match): A Match object corresponding to a shell command

        Returns:
            str: the output of the command
        """

        cmd_args = str(command.group(1))

        # TODO try/except; esacpe with shlex?
        cmd_output = subprocess.run(cmd_args, shell=True, capture_output=True, universal_newlines=True, encoding='utf-8')

        return cmd_output.stdout

    def process_tags_directive(self, tags: Match) -> str:
        """Convert a tag specification into a string containing inter-page links to
        pages marked with those tags. A tag specification is of the form '{{tag}}':

        -  `{{tag}}`: list all pages with 'tag'
        -  `{{tag1 tag2}}`: list all pages with 'tag1' or 'tag2'
        -  `{{tag1 &tag2}}`: list all pages with 'tag1' and 'tag2'
        -  `{{tag1 !tag2}}`: list all pages with 'tag1' but not 'tag2'
        -  `{{*}}`: list all pages in the namespace
        -  `{{@}}`: list all tags as bracketed spans with the CSS class given by
        the 'tag_css' configuration option
        -  `{{#}}`: return the total number of pages in the namespace, as an int
        -  `{{#tag}}`: return the number of pages with 'tag', as an int

        Note that in returned lists each link is separated by a blank line.
        
        If the first tag starts with a namespace alias (e.g. {{ns2:tag1}}) then this
        processing will act on that namespace's tags, generating relevant links. Subsequent
        tags should NOT start with a namespace alias.

        Args:
            tags (Match): A match object corresponding to a tag specification

        Returns:
            str: Markdown formatted link to page(s) whose tag match the
            specification
        """
        
        tag_list = str(tags.group(1))
        
        options = Page.TagListParser.parse(tag_list)

        # replace format. header if in template, else retain
        if options.format:
            options.format = self.namespace.config.templates.get(options.format, options.format)
            
        if options.header:
            options.header = self.namespace.config.templates.get(options.header, options.header)

        tag_list = options.tags

        # get initial category
        tag_name = tag_list[0].replace('_', ' ').lower()
        tag_text = ''

        # TODO if using format, then tag_text are the things that will go in there
        # default format is '' which means make, format does not apply to #, @ etc

        own_ns = False if ':' in tag_name else True
        
        if own_ns:
            tag_ns = self.namespace
        else:
            # tag in a different namespace
            tag_ns, _, tag_name = tag_name.partition(':')
            
            tag_ns = self.namespace.wiki.get_namespace(tag_ns)
            
            if not tag_ns:
                return tag_text

        if tag_name == '*':
            tag_text = [make_wiki_link(t, tag_ns.alias) for t in tag_ns.index.get_titles()]

        elif tag_name == '@':
            tag_text = [make_markdown_span(t, tag_ns.config.tags_css) for t in tag_ns.index.get_tags()]

        elif tag_name.startswith('#'):

            if tag_name == '#':
                tag_text = str(len(list(tag_ns.index.get_titles())))
            else:
                tag_text = str(len(tag_ns.index.get_tagged_pages(tag_name[1:])))
            
        elif tag_ns.index.has_tag(tag_name):
                # copy first tag set, which must exist
                # THIS returns page.title... NEEDS to be page so can get meta for format
                page_set = tag_ns.index.get_tagged_pages(tag_name)

                # add/del/combine other tagged categories
                for tag in tag_list[1:]:

                    tag_name = tag[1:] if tag.startswith(('&', '!')) else tag

                    # normalise tag name
                    tag_name = tag_name.lower()

                    if tag[0] == '&':
                        page_set = page_set & tag_ns.index.get_tagged_pages(tag_name)
                    elif tag[0] == '!':
                        page_set = page_set - tag_ns.index.get_tagged_pages(tag_name)
                    else:
                        page_set = page_set | tag_ns.index.get_tagged_pages(tag_name)

                ns_alias = '' if own_ns else tag_ns.alias
                
                if not options.format:
                    # TODO can't we just make a wiki link, as will be processed next?
                    tag_text = [make_markdown_link(p, '', ns_alias) for p in page_set]
                else:
                    # turn titles back into pages
                    page_set = [self.namespace.get_page(p) for p in page_set]

                    tag_text = [MetadataReplace(options.format).safe_substitute(p.meta) for p in page_set]

        else:
            pass
        
        if options.sort:
            # sort by content (e.g. title)
            tag_text = sorted(tag_text)
                
        tag_text = options.sep.join([options.before + 
                                     t + 
                                     options.after
                                     for t in tag_text])
        
        return options.header + tag_text

    def process_link_directives(self, page: Match, show_broken = True) -> str:
        """Convert a page title in double square brackets into an inter-page link.
        Typically this will be `[[Page name]]` or `[[Display name|Page name]]`,
        or with namespaces `[[ns:Page name]]` or `[[Display name|ns:Page name]]`.

        A page name should not contain a ":".
        
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

        # TODO the logic for handling names containing a ":" is a bit convoluted!
        # TODO suggest this is not allowed

        page_name = str(page.group(1))
        show_name = ''

        if '|' in page_name:
            show_name, _, page_name = page_name.partition('|')

        # resolve namespace
        namespace = ''
        page_title = page_name

        if ':' in page_name:
            # e.g. this is a [[x:Page One]] reference
            namespace, _, page_title = page_name.partition(':')

        # resolve namespace names or aliases to get target NS for the link
        if namespace:
            
            if namespace == '.':
                # use of [[.:Foo]] forces current namespace
                target_ns = self.namespace
            else:
                # lookup namespace alias
                target_ns = self.namespace.wiki.get_namespace(namespace)

            if not target_ns:
                # assume link is broken, as no target NS found
                logging.error(f"no namespace found using name or alias '{namespace}' for '{self.source}'")
                if show_broken:
                    return make_markdown_span(page_title, self.namespace.config.broken_css)
                else:
                    return page_title
        else:
            # no namespace given, look for page in all namespaces
            
            ### No namespace, see if exists locally THEN if not try to find....
            
            target_ns = self.namespace
            
            if not target_ns.get_page(page_name):
            
                search_page = self.namespace.wiki.get_page_by_name(page_name)
            
                if search_page:
                    # if this is a local page, we will find it here
                    target_ns = search_page.namespace
                else:
                    logging.debug(f"page '{self.source}' not found in any namespace")
                    if show_broken:
                        return make_markdown_span(page_title, self.namespace.config.broken_css)
                    else:
                        return page_title
                    
        # set show name if not already done
        if not show_name:
            show_name = page_title

        # resolve any alias for the title in the target index
        # TODO check that index has been created for that NS BEFORE using this
        # SO need better error message and catch exception and print directive and page
        if target_ns.index.has_alias(page_title):
            page_title = target_ns.index.get_alias(page_title)

        if target_ns.index.has_title(page_title):
            # if title exists in target namespace index make into a link
            ns_path = '' if target_ns is self.namespace else target_ns.name
            page_link = make_markdown_link(show_name, make_file_name(page_title), ns_path, target_ns.is_root)
        else:
            # if title does not exist in index then turn into bracketed span with class='broken' (default)
            page_link = make_markdown_span(page_title, target_ns.config.broken_css)
            target_ns.index.add_broken(page_title)

        return page_link

    def process_image_links(self, image: Match) -> str:
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

        return make_image_link(image_name, file_ext, self.media_dir)

    def process_custom_style(self, style: Match) -> str:
        """Convert a custom style specification into a (Pandoc) bracketed span.
        For example. `^^some text^^` becomes `[some text]{.smallcaps}`.

        Args:
            style (Match): A Match object corresponding to a custom style

        Returns:
            str: Pandoc bracketed span

        """

        style_text = str(style.group())[2:-2]

        return make_markdown_span(style_text, self.custom_css)

# TODO use mokuwiki --single
def mwpage(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Convert single Markdown file containing directives')
    parser.add_argument('source', help='Source file')
    parser.add_argument('target', help='Target file')
    parser.add_argument('--media', help='Name of media folder', default='images')
    parser.add_argument('--custom', help='String for custom CSS', default='.smallcaps')

    args = parser.parse_args(args)

    try:
        page = Page(args.source, None, media=args.media, custom=args.custom)
    except ValueError:
        print(f"could not create page {args.source}")
        sys.exit(0)
    
    page.process_directives()
    page.save(args.target)

# TODO is this needed?
def mwmeta(args=None):
    """This seems to have been an idea, but never used. It only qorks on metadata so Page may
    be unnecessary although useful. Maybe rewrite in Card.py"""

    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Output page metadata using template')
    parser.add_argument('template', help='Template string')
    parser.add_argument('sources', help='Source file(s)')
    parser.add_argument('--filter', default='', action='store', help='Filter on tags')

    args = parser.parse_args(args)

    keep_filter = set()
    drop_filter = set()    

    if args.filter:
        keep_filter = set([f for f in args.filter.split(',') if not f.startswith('!')])
        drop_filter = set([f[1:] for f in args.filter.split(',') if f.startswith('!')])

    files = Path('.') / args.sources

    files = sorted(set(glob.glob(os.path.normpath(os.path.join(os.getcwd(), args.sources)), recursive=True)))

    for file in files:
        try:
            page = Page(file, None)
        except ValueError:
            print(f"could not create page {file}")
            continue
        
        tags = set(page.meta['tags'])
        
        if args.filter and tags:
            if drop_filter and len(drop_filter.intersection(tags)) != 0:
                continue
            if keep_filter and len(keep_filter.intersection(tags)) != len(keep_filter):
                continue

        output = MetadataReplace(args.template).safe_substitute(page.meta)

        print(output + '\n')
