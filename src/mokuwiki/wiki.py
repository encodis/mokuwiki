import os
import sys
import argparse
import configparser

from mokuwiki.namespace import Namespace

import logging
logging.basicConfig(format='mokuwiki: %(levelname)s %(message)s', level=logging.WARNING)


class Wiki():
    """The Wiki class definition.

        An instance of a Wiki contains the overall (and default) configuration
        as well as instances of each namespace. Unless in "single file mode"
        the Wiki instance controls the creation of all namespaces, which, in
        turn, control the reading and creation of individual pages.
    """

    # NOTE should be singleton?

    def __init__(self, config_file, target='build', reindex=False, nosearch=False, verbose=0):
        """Initialize a Wiki instance.

        Args:
            config_file (FileType): The configuration file.
            target (str, optional): An optional target folder, overrides config file. Defaults to ''.
            reindex (bool, optional): Force re-indexing of all create_indexes. Defaults to False.
            nosearch (bool, optional): Stop creation of a search index. Defaults to False.
            verbose (int, optional): Increase verbose level. Defaults to 1.
        """

        # TODO could we just have properties to pull what we need out of config as required?

        config = configparser.ConfigParser()
        config.read(config_file)

        # set logging level to 20 (info), 30 (warn) or 40 (error)
        if not verbose:
            verbose = 0

        verbose = max(verbose, 3)

        self.verbose = config['DEFAULT'].getint('verbose', verbose)

        if self.verbose == 0:
            logging.getLogger().setLevel(logging.ERROR)
        elif self.verbose == 1:
            logging.getLogger().setLevel(logging.WARNING)
        elif self.verbose == 2:
            logging.getLogger().setLevel(logging.INFO)
        elif self.verbose == 3:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            pass

        self.wikiname = config['DEFAULT'].get('wikiname', 'Wiki')

        # default target path for each namespace, can be overidden by namespace initialization
        self.target = config['DEFAULT'].get('target', target)

        if not self.target:
            logging.warning(f"no target set for '{self.wikiname}', assuming 'build'")
            self.target = 'build'

        self.reindex = config['DEFAULT'].getboolean('reindex', reindex)

        self.broken_css = config['DEFAULT'].get('broken_css', '.broken')
        self.tags_css = config['DEFAULT'].get('tags_css', '.tags')
        self.custom_css = config['DEFAULT'].get('custom_css', '.smallcaps')

        self.search_fields = config['DEFAULT'].get('search_fields', 'title,alias,tags,summary,keywords')
        self.search_prefix = config['DEFAULT'].get('search_prefix', '')
        self.search_file = config['DEFAULT'].get('search_prefix', '_index.json')

        # override production of search index?
        # NOTE: this can be overriden by setting it for a specific namespace
        if nosearch:
            self.search_fields = ''

        # set default noise word list or file, will be read by each namespace
        self.noise_words = config['DEFAULT'].get('noise_words', '')

        # TODO auto-discover namespaces (if none specified in config) by looking
        # at sub-folders of wiki.path (or wiki.source?). No aliasese available
        # but would be easy. Also could we set defaults if no config file specified?

        # create namespaces
        self.namespaces = {}

        for section in config.sections():
            namespace = Namespace(config[section], self)

            if not namespace.valid:
                logging.warning(f"namespace '{namespace.name}' is invalid, skipping")
                continue

            if namespace.name in self.namespaces:
                logging.warning(f"namespace '{namespace.name}' already exists, skipping")
                continue

            if self.get_ns_by_alias(namespace.alias):
                logging.warning(f"namespace alias '{namespace.name}' already exists, skipping")
                continue

            self.namespaces[namespace.name] = namespace

        # TODO check for valid wiki here i.e. at least one valid namespace

    def __len__(self):
        """The 'size' of the wiki is the number of namespaces.

        Returns:
            int: Number of valid namespaces in wiki
        """
        return len(self.namespaces)

    # getitem for namespace lookup, by name or alias? ditto namespaces for pages?

    def get_ns_by_name(self, name):

        for namespace in self.namespaces:
            if name == self.namespaces[namespace].name:
                return self.namespaces[namespace]

        return None

    def get_ns_by_alias(self, alias):

        for namespace in self.namespaces:
            if alias == self.namespaces[namespace].alias:
                return self.namespaces[namespace]

        return None

    def get_page_path_by_link(self, page_link):
        """Get a page from a namespace by looking up
        the namespace alias and title.

        Example: "a:Foo" will return "aa/bb/foo.md" if the
        namespace alias "a" maps to the path "aa/bb"

        Args:
            page_link (str): Page link in format "a:Foo"
        """

        if ':' not in page_link:
            logging.warning(f"no namespace alias in '{page_link}'")
            return None

        ns_alias, page_title = page_link.split(':')
        namespace = self.get_ns_by_alias(ns_alias)
        page = namespace.get_page_by_title(page_title)

        return page.file

    def process_namespaces(self):
        """Process each namespace. First the namespaces are indexed,
        then the pages are processed.
        """

        for namespace in self.namespaces:
            self.namespaces[namespace].update_index()

        for namespace in self.namespaces:
            self.namespaces[namespace].process_pages()

    def report_broken_links(self):
        """Report broken links. If the verbose level is set
        to 3 then report broken links.
        """

        # if logging.getLogger().getEffectiveLevel() < logging.ERROR:
        #     return

        for namespace in self.namespaces:
            if len(self.namespaces[namespace].index.broken) == 0:
                continue

            for page_name in self.namespaces[namespace].index.broken:
                logging.info(f'broken link: {self.namespaces[namespace].name}:{page_name}')


def mokuwiki(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Convert folder of Markdown files to support interpage linking and tags')
    parser.add_argument('config', help='Wiki configuration file')
    parser.add_argument('--target', help='Target directory root')
    parser.add_argument('--reindex', help='Force reindex', action='store_true')
    parser.add_argument('--nosearch', help='Do not produce a search index (JSON)', action='store_true')
    parser.add_argument('-v', '--verbose', help='Set logging verbosity', action='count')

    args = parser.parse_args(args)

    wiki = Wiki(args.config, target=args.target, reindex=args.reindex, nosearch=args.nosearch, verbose=args.verbose)

    if len(wiki) == 0:
        logging.error(f"wiki '{wiki.name}' has no valid namespaces")
        exit(1)

    wiki.process_namespaces()
    wiki.report_broken_links()
