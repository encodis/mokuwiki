import re
import json
import datetime
import logging
from pathlib import Path
from collections import defaultdict
from typing import TYPE_CHECKING

from mokuwiki.page import Page
from mokuwiki.utils import make_file_name

if TYPE_CHECKING:
    from mokuwiki.namespace import Namespace


class Index:
    """A class containing the various indexes required by a namespace.
    """

    def __init__(self, namespace: 'Namespace') -> None:
        """Initialize an Index instance

        Args:
            namespace (Namespace): the parent namespace.
        """

        self.namespace = namespace

        # note: not the name of the exported JSON file! used in save()
        self.name = '_' + self.namespace.name + '.idx'
        """
        need self._titles then property .titles lists the _titles.keys()
        also a specific add_page() method to add a page - could call _update_xxx
        
        then has_title() and has_alias()
        """
        # TODO check if saved index exists and is older than mtime of ns path
        self._titles = {} # a map of titles (from page meta) to targets (i.e. slugified title for output)
        self._aliases = {} # a map of aliases to titles
        self._tags = defaultdict(set) # a map of tags by page title
        self._broken = set()
        self._search = defaultdict(list)

        self.modified = datetime.datetime.now()

    def save(self) -> None:
        pass

    def add_page(self, page: Page) -> None:
        
        if self.has_title(page.title):
            logging.warning(f"skipping '{page.source}', duplicate title '{page.title}'")
            raise ValueError
        
        if self.has_target(page.target):
            logging.warning(f"skipping '{page.source}', duplicate output filename '{page.target}'")
            raise ValueError
        
        if page.alias:
            if self.has_alias(page.alias):
                logging.warning(f"skipping '{page.file}', duplicate alias '{page.alias}'")
                raise ValueError
            
            if page.alias in self._titles:
                logging.warning(f"skipping '{page.file}', alias duplicated in title of '{self._titles[page.alias]}'")
                raise ValueError

        self._titles[page.title] = page.target
        self._aliases[page.alias] = page.title

        # TODO need a consistent function to remove [] and lower case etc, slugify?
        # TODO should tags be lowercased for these purposes???
        for tag in page.tags:
            self._tags[tag.replace('[', '').replace(']', '').lower()].add(page.title)

        self._update_search_index(page)

    def has_title(self, page_name: str) -> bool:
        return True if page_name in self._titles.keys() else False

    def has_alias(self, page_name: str) -> bool:
        return True if page_name in self._aliases.keys() else False

    def has_tag(self, tag_name: str) -> bool:
        tag_name = tag_name.replace('[', '').replace(']', '').lower()
        
        return True if tag_name in self._tags.keys() else False
    
    def has_target(self, target: str) -> bool:
        return True if target in self._titles.values() else False
    
    def get_target_by_title(self, title: str) -> str|None:
        return self._titles[title] if title in self._titles else None
    
    def get_title_by_alias(self, alias: str) -> str|None:
        return self._aliases[alias] if alias in self._aliases else None
    
    def get_alias(self, page_name: str) -> str:
        return self._aliases[page_name] if self.has_alias(page_name) else ''
    
    def get_titles(self) -> list[str]:
        return self._titles.keys()
    
    def get_tags(self) -> list[str]:
        return self._tags.keys()


    def get_tagged_pages(self, tag_name: str) -> set|None:
        if not self.has_tag(tag_name):
            return set()
        
        return self._tags[tag_name]

    def add_broken(self, broken_name: str) -> None:
        self._broken.add(broken_name)
        
    def get_broken(self) -> set:
        return self._broken

    def _update_search_index(self, page: Page) -> None:
        """Update the search index with strings extracted from metadata in a
        Markdown file. If the file's metadata contains the key 'noindex' with
        the value 'true' then the file will not be indexed, regardless of
        other settings.

        Args:
            page (Page): The page to be indexed
        """

        # test for 'noindex' metadata
        if page.noindex:
            return

        if not self.namespace.config.search_fields:
            return

        terms = ''

        for field in self.namespace.config.search_fields:

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
        terms = [term for term in terms.split() if term not in self.namespace.config.noise_words]

        # update index of unique terms
        for term in list(set(terms)):
            self._search[term].append((make_file_name(page.title), page.title))

    def export_search_index(self) -> None:
        """Save the search index as a JSON file. The file name is given
        by the 'search_file' configuration option.
        """
        search_index = self.namespace.config.search_prefix + json.dumps(self._search, indent=2)

        with Path(self.namespace.config.target_dir / self.namespace.config.search_file).open('w', encoding='utf8') as jf:
            jf.write(search_index)
