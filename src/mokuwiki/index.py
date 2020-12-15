import os
import re
import json
import datetime
import logging

from collections import defaultdict


class Index():
    """A class containing the various indexes required by a
    namespace.
    """

    def __init__(self, namespace):
        """Initialize an Index instamce

        Args:
            namespace (Namespace): the parent namespace.
        """

        self.namespace = namespace

        # note: not the name of the exported JSON file!
        self.name = '_' + self.namespace.name + '.idx'

        # TODO check if saved index exists and is older than mtime of ns path
        self.title = {}
        self.alias = {}
        self.tags = defaultdict(set)
        self.broken = set()
        self.search = defaultdict(list)

        self.modified = datetime.datetime.now()

    def save(self):
        pass

    def update_title(self, page):
        """Update the index of page titles.

        Args:
            page (Page): The page to index
        """

        if page.title in self.title:
            logging.warning(f"skipping '{page.file}', duplicate title '{page.title}'")
            page.valid = False
            return

        self.title[page.title] = page.output

    def update_alias(self, page):
        """Update the index of page aliases, if the page has one.

        Args:
            page (Page): The page to index
        """

        if not page.alias:
            return

        if page.alias in self.alias:
            logging.warning(f"duplicate alias '{page.alias}', in file '{page.file}', compare to '{self.alias[page.alias]}'")
            return

        if page.alias in self.title:
            logging.warning(f"duplicate title '{page.alias}', in file '{page.file}', compare to '{self.title[page.alias]}'")
            return

        self.alias[page.alias] = page.title

    def update_tags(self, page):
        """Update the index of tags.

        Args:
            page (Page): The page to index
        """

        if 'tags' not in page.meta:
            return

        for tag in page.meta['tags']:
            self.tags[tag.replace('[', '').replace(']', '').lower()].add(page.title)

    def update_search(self, page):
        """Update the search index with strings extracted from metadata in a
        Markdown file. If the file's metadata contains the key 'noindex' with
        the value 'true' then the file will not be indexed, regardless of
        other settings.

        Args:
            page (Page): The page to be indexed
        """

        if not page.valid:
            return

        # test for 'noindex' metadata
        if page.meta.get('noindex', False):
            return

        if not self.namespace.search_fields:
            return

        terms = ''

        for field in self.namespace.search_fields:

            if field == '_body_':
                terms += ' ' + page.body

            if page.meta.get(field, False):

                if isinstance(page.meta[field], str):
                    terms += ' ' + page.meta[field]
                elif isinstance(page.meta[field], list):
                    # if field is a list, convert to string before adding
                    terms += ' ' + ' '.join(page.meta[field])
                else:
                    logging.warning(f"unknown metadata type '{field}' in page '{page.title}'")

        # remove punctuation etc from YAML values, make lower case
        terms = re.sub('[^a-z0-9 ]', '', terms.lower())

        # remove noise words
        terms = [term for term in terms.split() if term not in self.namespace.noise_words]

        # update index of unique terms
        for term in list(set(terms)):
            self.search[term].append((self.title[page.title], page.title))

    def export_search_index(self):
        """Save the search index as a JSON file. The file name is given
        by the 'search_file' configuration option.
        """
        search_index = self.namespace.search_prefix + json.dumps(self.search, indent=2)

        with open(os.path.join(self.namespace.target, self.namespace.search_file), 'w', encoding='utf8') as jf:
            jf.write(search_index)
