import os
import glob
import logging

import mokuwiki.page as p
from mokuwiki.index import Index

DEFAULT_NOISE_WORDS = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for',
                       'if', 'i', 'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on',
                       'or', 'such', 'that', 'the', 'their', 'then', 'there', 'these',
                       'they', 'this', 'to', 'was', 'will', 'with']


class Namespace():
    """The Namespace class definition.

    An instance of a namespace contains the pages in the namespace, their index
    and any namespace related configuration. The namespaces controls the
    creation and processing of all pages (unless a page has been created in
    "single file" mode).
    """

    def __init__(self, config, wiki):
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

        # set reference to parent Wiki
        self.wiki = wiki

        # get namespace name, if none use name of config section
        # TODO use p.slugify() in case of spaces in name?
        self.name = config.get('name', config.name.lower())

        # get namespace alias, if none then use name of namespace
        self.alias = config.get('alias', self.name.lower())

        # check path exists
        self.path = config.get('path', '')
        # self.path = config.get('path', f"{content_dir}/{self.name}/{pages_dir}")

        if not self.path or not os.path.isdir(self.path):
            logging.warning(f"namespace path '{self.path}' does not exist, skipping")
            self.valid = False
            # TODO raise execption and have caller catch it
            return

        # is root namespace?
        self.is_root = True if config.get('is_root', '') == 'true' else False

        # set target, default target root will be wiki target
        self.target = config.get('target', '')
        self.target = os.path.join(self.target, self.name)

        # create target path
        try:
            os.makedirs(self.target, exist_ok=True)
        except IOError:
            logging.error(f"cannot create target path '{self.target}' for namespace '{self.name}'")

        # set config parameters
        self.media_dir = config.get('media_dir', 'images')

        self.broken_css = config.get('broken_css', '.broken')
        self.tags_css = config.get('tags_css', '.tags')
        self.custom_css = config.get('custom_css', '.smallcaps')
        self.noise_tags = config.get('noise_tags', '').split(',')

        self.search_fields = config.get('search_fields', False)

        if self.search_fields:
            self.search_fields = [f.strip() for f in self.search_fields.split(',')]

        self.search_prefix = config.get('search_prefix', '')
        self.search_file = config.get('search_file', '_index.json')

        # noise words inherit from wiki config, but still evaluate for each namespace
        noise_words = config.get('noise_words', '')

        self.noise_words = self.get_noise_words(noise_words)

        self.meta_fields = config.get('meta_fields', False)

        if self.meta_fields:
            self.meta_fields = [f.strip() for f in self.meta_fields.split(',')]

        self.pages = []

        self.index = Index(self)

        # TODO test support for '**' in glob spec, with recursive=True
        # titles must be unique? or allow path to be multivalued
        # or ensure there is a pre stage that copies the files in the build file, then they would
        # need to be unique
        for page_file in glob.glob(os.path.join(os.path.normpath(self.path), '*.md')):
            # pass in ref to namespace
            page = p.Page(page_file, self)

            if page.valid:
                self.pages.append(page)

        self.valid = True
        self.modified = os.path.getmtime(self.path)

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

    def get_noise_words(self, noise_words):
        """Create a list of noise words to remove from the search index.
        Defaults to the constant DEFAULT_NOISE_WORDS in this module. If the
        string starts with the substring "file:" then the remainder of the
        string is used as a file name to load the noise words. This file
        should be a plain text file with one word per line.

        Args:
            noise_words (str): Comma separated list of noise words, or file
            specification.

        Returns:
            list: List of noise words.
        """

        if not noise_words:
            return DEFAULT_NOISE_WORDS

        if noise_words.startswith('file:'):
            noise_file = noise_words[5:]

            if not os.path.isabs(noise_file):
                noise_file = os.path.join(self.path, noise_file)

            try:
                with open(noise_file, 'r', encoding='utf8') as nf:
                    return nf.read().split('\n')
            except IOError:
                logging.error(f"could not open noise word file '{noise_words[5:]}'")
                return ''

        # comma separated list of strings
        return [n.strip() for n in noise_words.split(',')]

    def update_index(self):
        """Update the Index instance for this namespace. This should
        be called before processing the pages.
        """

        for page in self.pages:

            self.index.update_title(page)

            if not page.valid:
                continue

            self.index.update_alias(page)
            self.index.update_tags(page)

            if self.search_fields:
                self.index.update_search(page)

    def process_pages(self):
        """Process each page, first processing any embedded directives,
        then outputting the result to the namespace's target.
        """

        for page in self.pages:
            page.process_directives()
            page.save()

        if self.search_fields:
            self.index.export_search_index()
