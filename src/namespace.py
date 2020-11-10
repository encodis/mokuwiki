"""Namespace class

can we assume that, as the wiki is supposed to be coherent, we don't do the fullns stuff?
which was for nested namespaces? so ANY namespace ref will be ../xxx/foo.html etc

i.e. we will ALWAYS use a ns alias to refer to a namespace...

"""

import os
import re
import glob
import json
import datetime

from collections import defaultdict

import page as p


class Namespace():

    def __init__(self, config, wiki):

        # config is a dict like object, e.g. config parser section
        # ns may be created on the fly by page, so may not have config objects
        # then it will not have a path, as it not loading 
        
        # get namespace name, if none use name of config section
        self.name = config.get('name', config.name.lower())

        # get namespace alias, if none then use name of namespace
        self.alias = config.get('alias', self.name.lower())

        # check path exists
        # TODO how does it interact with wiki.target?
        self.path = config['path']

        if not self.path or not os.path.isdir(self.path):
            print(f'mokuwiki: namespace path {self.path} does not exist, skipping')
            self.valid = False
            return

        self.media = config.get('media', 'images')
        self.modified = os.path.getmtime(self.path)

        # set reference to parent Wiki
        self.wiki = wiki

        self.pages = []

        # TODO may need a 'timestamped' index that has timestamp for each key, but dict() API
        self.index = Index(self)

        for page_file in glob.glob(os.path.normpath(self.path) + '*.md'):
            # pass in ref to namespace
            page = p.Page(page_file, self)

            if page.valid:
                self.pages.append(page)
                
            # TODO keep an index of page/path and last updated time
            # need to keep timestamp for when index was made but also need backrefs of pages
            # OR can we do on a 'has namespace' changed basis, mod time of folder

    def __len__(self):
        return len(self.pages)

    def update_index(self):
        # FIXME create indexes over all self.pages
        # ALSO this will check for duplicate titles, aliases etc
        for page in self.pages:

            self.index.update_title(page)

            if not page.valid:
                continue

            self.index.update_alias(page)
            self.index.update_tags(page)

            if self.search_index:
                self.index.update_search(page)

    def process_pages(self):

        for page in self.pages:
            page.process_directives()
            page.save()

        if self.search_index:
            self.index.export_search_index()


class Index():

    def __init__(self, namespace):

        self.modified = datetime.datetime.now()
        self.namespace = weakref.ref(namespace)

        self.name = '_' + self.namespace.name + '.index'

        self.title = {}
        self.alias = {}
        self.tags = defaultdict(set)
        self.broken = set()
        self.search = defaultdict(list)

    def save(self):
        pass

    def update_title(self, page):
        if page.title not in self.title:
            self.title[page.title] = page.output
        else:
            print(f"mokuwiki: skipping '{page.file}', duplicate title '{page.title}'")
            page.valid = False

    def update_alias(self, page):
        # get alias, if any
        if page.alias:
            if page.alias not in self.alias and page.alias not in self.title:
                self.alias[page.alias] = page.title
            else:
                print(f"mokuwiki: duplicate alias '{page.alias}', in file '{page.file}'")

    def update_tags(self, page):
        for tag in page.meta.tags:
            self.tags[tag.replace('[', '').replace(']', '').lower()].add(page.title)

    def update_search(self, page):
        """Update the search index with strings extracted from metadata in a
        Markdown file. If the file's metadata contains the key 'noindex' with the
        value 'true' then the file will not be indexed.

        Args:
            contents (str): the entire contents of the Markdown file, including metadata
            title (str): the title of the document

        Returns:
            None

        """

        if not page.valid:
            return

        # test for 'noindex' metadata
        if page.meta.get('noindex', False):
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
                    print(f"mokuwiki: unknown metadata type '{field}' in page: '{page.title}'")

        # remove punctuation etc from YAML values, make lower case
        terms = re.sub('[^a-z0-9 ]', '', terms.lower())

        # remove noise words
        terms = [term for term in terms.split() if term not in self.namespace.noise_words]

        # update index of unique terms
        for term in list(set(terms)):
            self.search[term].append((self.title[page.title], page.title))

    def export_search_index(self, file_name='_index.json'):
        
        # write out search index (unless in single file mode)
        search_index = self.namespace.search_prefix + json.dumps(self.search, indent=2)

        with open(os.path.join(self.wiki.target, self.name, file_name), 'w', encoding='utf8') as json_file:
            json_file.write(search_index)
