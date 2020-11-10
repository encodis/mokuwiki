"""Wiki class

contains namespaces and overall config

wiki config file required, makes arg parsing easier 

with config parser, default section is defaults applied to each section

"""

import sys
import argparse
import configparser

from namespace import Namespace

DEFAULT_NOISE_WORDS = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for',
                       'if', 'i', 'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on',
                       'or', 'such', 'that', 'the', 'their', 'then', 'there', 'these',
                       'they', 'this', 'to', 'was', 'will', 'with']


class Wiki():

    # NOTE should be singleton?

    def __init__(self, config, options):

        # in single file mode don't need most of these? maybe only need a Page, then process it

        config = configparser.ConfigParser(config)

        self.name = config['DEFAULT'].get('name', 'Wiki')
        self.root = config['DEFAULT'].get('root', '.')
        self.target = config['DEFAULT'].get('target', '')
        
        if options.get('reindex', ''):
            pass
        if options.get('report', ''):
            pass
        if options.get('verbose', ''):
            pass
        
        if not self.target:
            self.target = options.get('target', '')
            
            if not self.target:
                print(f"mokuwiki: no target set for wiki '{self.name}'")
        
        self.broken_css = config['DEFAULT'].get('broken_css', '.broken')
        self.tags_css = config['DEFAULT'].get('tags_css', '.tags')
        self.custom_css = config['DEFAULT'].get('custom_css', '.smallcaps')
        self.incl_replace = config['DEFAULT'].get('incl_replace', True)
        
        self.search_index = config['DEFAULT'].get('search_index', False)
        
        if options.get('nosearch', ''):
            self.search_index = False
        
        self.search_fields = config['DEFAULT'].get('search_fields', 'title,alias,tags,summary,keywords')
        self.search_prefix = config['DEFAULT'].get('search_prefix', '')

        self.noise_words = config['DEFAULT'].get('noise_words', DEFAULT_NOISE_WORDS)

        self.namespaces = {}

        for section in config.sections():
            namespace = Namespace(section, self)

            if not namespace.valid:
                print(f"mokuwiki: namespace '{namespace.name}' is invalid, skipping")
                continue

            if namespace.name in self.namespaces:
                print(f"mokuwiki: namespace '{namespace.name}' already exists, skipping")
                continue

            if self.ns_alias(namespace.alias):
                print(f"mokuwiki: namespace alias '{namespace.name}' already exists, skipping")
                continue

            self.namespaces[namespace.name] = namespace

    ## check no clashes with NS names or aliases

    def __len__(self):
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
                return namespace

        return None

    def process_namespaces(self):

        for namespace in self.namespaces:
            namespace.update_index()
            namespace.process_pages()


def mokuwiki(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Convert folder of Markdown files to support interpage linking and tags')
    parser.add_argument('config', help='Wiki configuration file')
    parser.add_argument('target', help='Target directory root', required=False)
    parser.add_argument('--reindex', help='Force reindex')
    parser.add_argument('--nosearch', help='Do not produce a search index (JSON)', action='store_true', default=False)
    # should be --search _index.json as default but how to turn off?
    parser.add_argument('--report', help='Report broken links', action='store_true', default=False)
    parser.add_argument('--verbose', help='Output current file and task', action='store_true', default=False)

    args = parser.parse_args(args)

    wiki = Wiki(args.config, vars(args))
        
    if len(wiki) == 0:
        print(f"mokuwiki: wiki '{wiki.name}' has no valid namespaces")
        exit(1)
        
    wiki.process_namespaces()
