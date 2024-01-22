import sys
import argparse

from mokuwiki.config import WikiConfig
from mokuwiki.namespace import Namespace

import logging
logging.basicConfig(format='mokuwiki: %(levelname)s %(message)s', level=logging.WARNING)


class Wiki:
    """The Wiki class definition.

        An instance of a Wiki contains the overall (and default) configuration
        as well as instances of each namespace. Unless in "single file mode"
        the Wiki instance controls the creation of all namespaces, which, in
        turn, control the reading and creation of individual pages.
    """

    # NOTE should be singleton?

    def __init__(self, config, reindex=False, nosearch=False, verbose=1):
        """Initialize a Wiki instance.

        Args:
            config (FileType or dict): The configuration file or dictionary.
            reindex (bool, optional): Force re-indexing of all create_indexes. Defaults to False.
            nosearch (bool, optional): Stop creation of a search index. Defaults to False.
            verbose (int, optional): Increase verbose level. Defaults to 1.
        """
        
        self.config = WikiConfig(config)
        
        self._set_reporting_level(verbose)
        
        # create namespaces
        self.namespaces = {}

        self.root_ns = None
        
        for name, config in self.config.namespaces.items():
            
            try:
                namespace = Namespace(name, config, self)
            except ValueError:
                logging.error(f"namespace {name} could not be created")
                continue
            
            if namespace.is_root and self.root_ns:
                logging.warning(f"namespace '{namespace.name}' claims to be root, as does '{self.root_ns}, skipping")
                continue
                
            self.root_ns = namespace.name
            
            if namespace.name in self.namespaces:
                logging.warning(f"namespace '{namespace.name}' already exists, skipping")
                continue

            if self.get_ns_by_alias(namespace.alias):
                logging.warning(f"namespace alias '{namespace.alias}' already exists, skipping")
                continue

            self.namespaces[namespace.name] = namespace
            
        if not self.root_ns:
            logging.error(f"no namespace has been marked as root")
            
        if len(self.namespaces) == 0:
            logging.error(f"no valid namespaces found")

    def __len__(self):
        """The 'size' of the wiki is the number of namespaces.

        Returns:
            int: Number of valid namespaces in wiki
        """
        return len(self.namespaces)

    # getitem for namespace lookup, by name or alias? ditto namespaces for pages?

    def _set_reporting_level(self, verbose):
        if not verbose:
            verbose = self.config.verbose

        self.verbose = verbose

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

    def get_ns_by_name(self, name):

        # [ns[namespace] for ns in self.namespaces if name == ns.name]

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

        ns_alias, page_title = page_link.split(':', 1)
        namespace = self.get_ns_by_alias(ns_alias)
        
        if not namespace:
            logging.error(f"no namespace found for alias '{ns_alias}'")
            return None
        
        page = namespace.get_page_by_title(page_title)

        if not page:
            logging.error(f"no page titled '{page_title}' in namespace '{namespace.name}'")
            return None

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