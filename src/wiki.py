import sys
import argparse
import configparser

from namespace import Namespace

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

    def __init__(self, config_file, target='', reindex=False, nosearch=False, verbose=1):
        """Initialize a Wiki instance.

        Args:
            config_file (FileType): The configuration file.
            target (str, optional): An optional target folder, overrides config file. Defaults to ''.
            reindex (bool, optional): Force re-indexing of all create_indexes. Defaults to False.
            nosearch (bool, optional): Stop creation of a search index. Defaults to False.
            verbose (int, optional): Increase verbose level. Defaults to 1.
        """

        if verbose:
            # set logging level to 20 (info), 30 (warn) or 40 (error)
            verbose = 10 + max(verbose, 3) * 10
            logging.getLogger().setLevel(verbose)

        # TODO could we just have properties to pull what we need out of config as required?

        config = configparser.ConfigParser()
        config.read(config_file)

        self.wikiname = config['DEFAULT'].get('name', 'Wiki')

        # default target path for each namespace, can be overidden by namespace initialization
        self.target = config['DEFAULT'].get('target', target)

        if not self.target:
            logging.warning(f'no target set for {self.wikiname}')

        self.verbose = config['DEFAULT'].get('verbose', verbose)

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

            if self.ns_alias(namespace.alias):
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

    def ns_exists(self, alias):

        for namespace in self.namespaces:
            if alias == self.namespaces[namespace].alias:
                return True

        return False

    def ns_alias(self, alias):

        for namespace in self.namespaces:
            if alias == self.namespaces[namespace].alias:
                return self.namespaces[namespace]

        return None

    def process_namespaces(self):
        """Process each namespace. First the namespaces are indexed,
        then the pages are processed.
        """

        for namespace in self.namespaces:
            self.namespaces[namespace].update_index()

        for namespace in self.namespaces:
            self.namespaces[namespace].process_pages()

    def report_broken_links(self):
        """Report broken links. This will set the logging level
        to "ERROR" to ensure output, as it has been explicitly
        requested.
        """
        logging.getLogger().setLevel(logging.ERROR)

        for namespace in self.namespaces:
            if not namespace.index.broken:
                continue

            for page_name in namespace.index.broken:
                logging.error(f'broken link: {namespace.name}:{page_name}')


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
