from pathlib import Path
import logging

import mokuwiki.page as p
from mokuwiki.config import NamespaceConfig
from mokuwiki.index import Index


class Namespace:
    """The Namespace class definition.

    An instance of a namespace contains the pages in the namespace, their index
    and any namespace related configuration. The namespaces controls the
    creation and processing of all pages (unless a page has been created in
    "single file" mode).
    """

    def __init__(self, name, config, wiki):
        """Initialize a Namespace instance. The main 'config' parameter is intended
        to be a ConfigParser section object, which behaves in a similar way to
        a dictionary. If, for any reason, a configuration option causes the
        namespace to be invalid in some way then the namespace will set a
        'valid' member attribute to 'False' and return. This value should be
        checked before using the namespace.

        Note: ConfigParser section objects refer to the 'DEFAULT' section
        for parameter values if they do not contain the key themselves.
        Specifying a specific key in a namespace config section will
        override that in the default section.

        Args:
            config (ConfigParser): A section of a config file, read by
            ConfigParser
            wiki (Wiki): A reference to the namespace's parent wiki.
        """

        self.config = NamespaceConfig(name, config, wiki)

        self.wiki = wiki
        
        # for convenience...
        self.name = self.config.name
        self.alias = self.config.alias

        if not self.config.content or not Path(self.config.content).is_dir():
            logging.warning(f"namespace path '{self.config.content}' does not exist, skipping")
            raise ValueError

        self.is_root = self.config.is_root

        # create target path
        self.config.target.mkdir(parents=True, exist_ok=True)
        # os.makedirs(self.config.target, exist_ok=True)
        
        self.index = Index(self)

        # TODO test support for '**' in glob spec, with recursive=True
        # titles must be unique? or allow path to be multivalued
        # or ensure there is a pre stage that copies the files in the build file, then they would
        # need to be unique

        self.pages = []
        
        for page_path in self.config.content.glob('*.md'):
        # for page_file in glob.glob(os.path.join(os.path.normpath(self.config.content), '*.md')):
            # pass in ref to namespace
            try:
                page = p.Page(page_path, self)
            except ValueError:
                logging.error(f"page {page_path} could not be created")
                continue
            
            self.pages.append(page)

        # self.modified = os.path.getmtime(self.config.target)
        self.modified = self.config.target.stat().st_mtime

        logging.info(f"created namespace '{self.name}'")

    def __len__(self):
        """The 'size' of the namespace is the number of pages.

        Returns:
            int: Number of valid pages in wiki
        """
        return len(self.pages)

    def get_page_by_title(self, page_title):
        """Get a reference to a page given the page title.
        If no titles match then try aliases.

        Args:
            page_title (str): The page title (case sensitive)
        """
        
        for page in self.pages:
            if page.title == page_title:
                return page

        # if still here try aliases
        for page in page.alias:
            if page.alias == page_title:
                return page

    def update_index(self):
        """Update the Index instance for this namespace. This should
        be called before processing the pages.
        """

        for page in self.pages:

            self.index.update_title(page)
            self.index.update_alias(page)
            self.index.update_tags(page)

            if self.config.search_fields:
                self.index.update_search(page)

    def process_pages(self):
        """Process each page, first processing any embedded directives,
        then outputting the result to the namespace's target.
        """

        for page in self.pages:
            page.process_directives()
            page.save()

        if self.config.search_fields:
            self.index.export_search_index()
