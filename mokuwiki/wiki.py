import argparse
import shutil
import sys

from mokuwiki.config import WikiConfig
from mokuwiki.namespace import Namespace
from mokuwiki.page import Page
from mokuwiki.process import Processor

import logging
logging.basicConfig(format='mokuwiki: %(levelname)s %(message)s', level=logging.WARNING)


class Wiki:
    """The Wiki class definition.

        An instance of a Wiki contains the overall (and default) configuration
        as well as instances of each namespace. Unless in "single file mode"
        the Wiki instance controls the creation of all namespaces, which, in
        turn, control the reading and creation of individual pages.
    """
    
    def __init__(self, config: dict | str, verbose: int = 1) -> str:
        """Initialize a Wiki instance.

        Args:
            config (FileType or dict): The configuration file or dictionary.
            reindex (bool, optional): Force re-indexing of all create_indexes. Defaults to False.
            nosearch (bool, optional): Stop creation of a search index. Defaults to False.
            verbose (int, optional): Increase verbose level. Defaults to 1.
        """
        try:
            self.config = WikiConfig(config)
        except ValueError:
            raise ValueError("Could not initialize wiki")
                
        self._set_reporting_level(verbose)
        
        # set up build dir
        if self.config.clean in ['setup', 'always']:
            shutil.rmtree(self.config.build_dir, ignore_errors=True)
            
        self.config.build_dir.mkdir(parents=True, exist_ok=True)
        
        # create namespaces
        self.namespaces = {}

        self.root_ns = None
        
        for name, ns_config in self.config.namespaces.items():
            
            try:
                namespace = Namespace(name, ns_config, self)
            except ValueError:
                logging.error(f"namespace {name} could not be created")
                continue
            
            if namespace.is_root and self.root_ns:
                logging.warning(f"namespace '{namespace.name}' claims to be root, as does '{self.root_ns}, skipping")
                continue
                
            self.root_ns = namespace.name
            
            if self.get_namespace(namespace.name):
                logging.warning(f"namespace '{namespace.name}' already exists, skipping")
                continue

            if self.get_namespace(namespace.alias):
                logging.warning(f"namespace alias '{namespace.alias}' already exists, skipping")
                continue

            self.namespaces[namespace.name] = namespace
                    
        if not self.root_ns:
            logging.error(f"no namespace has been marked as root")
            
        if len(self.namespaces) == 0:
            logging.error(f"no valid namespaces found")

        self.processor = Processor()

    def __len__(self) -> int:
        """The 'size' of the wiki is the number of namespaces.

        Returns:
            int: Number of valid namespaces in wiki
        """
        return len(self.namespaces)

    # getitem for namespace lookup, by name or alias? ditto namespaces for pages?

    def _set_reporting_level(self, verbose: int) -> None:
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

    def get_namespace(self, name: str) -> str | None:
        """Get a namespace from its full name or alias.
        """
        
        if name in self.namespaces:
            return self.namespaces[name]

        # now check aliases        
        for namespace in self.namespaces:
            if name == self.namespaces[namespace].alias:
                return self.namespaces[namespace]
            
        return None

    def get_page_by_name(self, page_name: str) -> Page | None:
        """Get a page from a namespace by looking up the namespace alias and title.

        Example: "a:Foo" will return "aa/foo.md" if the namespace alias "a" maps to the path "aa/"

        Args:
            page_name (str): Page name in format "a:Foo" or just "Foo" (to search all namespaces)
            
        Returns:
            Page: the relevant Page object, or None if not found
        """

        if ':' not in page_name:
            # search all namespaces, return first match
            # TODO what about same page title in diff NS, how to select?
            
            for _, namespace in self.namespaces.items():
                page = namespace.get_page(page_name)
                
                if page:
                    return page
            
            return None

        ns_alias, _, page_name = page_name.partition(':')
        namespace = self.get_namespace(ns_alias)
        
        if not namespace:
            logging.error(f"no namespace found for alias '{ns_alias}'")
            return None
        
        page = namespace.get_page(page_name)

        if not page:
            logging.error(f"no page titled '{page_name}' in namespace '{namespace.name}'")
            return None

        return page

    def process_wiki(self) -> None:
        """Note: need the separate loops
        """
        
        logging.info("processing wiki")

        for namespace in self.namespaces:
            self.namespaces[namespace].preprocess_pages()
            self.namespaces[namespace].load_pages()

        for namespace in self.namespaces:
            self.namespaces[namespace].process_pages()
            
        for namespace in self.namespaces:
            self.namespaces[namespace].postprocess_pages()

        # tear down build dir
        if self.config.clean in ['teardown', 'always']:
            shutil.rmtree(self.config.build_dir, ignore_errors=False)

    def report_broken_links(self) -> None:
        """Report broken links in namespaces.
        """

        for namespace in self.namespaces:
            self.namespaces[namespace].report_broken_links()


def mokuwiki(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Convert folder of Markdown files to support interpage linking and tags')
    parser.add_argument('config', help='Wiki configuration file')
    parser.add_argument('-v', '--verbose', help='Set logging verbosity', action='count')

    args = parser.parse_args(args)

    wiki = Wiki(args.config, verbose=args.verbose)

    if len(wiki) == 0:
        logging.error(f"wiki '{wiki.name}' has no valid namespaces")
        exit(1)

    wiki.process_wiki()
    wiki.report_broken_links()
