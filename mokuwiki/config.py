from pathlib import Path
import logging

import yaml

DEFAULT_WIKINAME = 'Wiki'
DEFAULT_TARGET = 'build'
DEFAULT_VERBOSITY = 1
DEFAULT_REINDEX = False
DEFAULT_BROKEN_CSS = '.broken'
DEFAULT_TAGS_CSS = '.tag'
DEFAULT_CUSTOM_CSS = '.smallcaps'
DEFAULT_CONTENT_DIR = 'content'
DEFAULT_PAGES_DIR = 'pages'
DEFAULT_MEDIA_DIR = 'images'
DEFAULT_SEARCH_FIELDS = ['title', 'alias', 'tags', 'summary', 'keywords']
DEFAULT_SEARCH_PREFIX = ''
DEFAULT_SEARCH_FILE = '_index.json'

DEFAULT_NOISE_WORDS = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for',
                       'if', 'i', 'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on',
                       'or', 'such', 'that', 'the', 'their', 'then', 'there', 'these',
                       'they', 'this', 'to', 'was', 'will', 'with']

class WikiConfig:
    
    def __init__(self, config):
        
        if isinstance(config, dict):
            self.config = config
        elif isinstance(config, str):
            with Path(config).open('r') as cf:
                try:
                    self.config = yaml.safe_load(cf)
                except yaml.YAMLError:
                    # might occur for duplicated namespace names
                    logging.error(f"Error reading config file {config}")
                    return
        else:
            logging.error(f"Bad configuration {config}")
    
    @property
    def name(self) -> str:
        return self.config.get('name', DEFAULT_WIKINAME)
    
    @property
    def namespaces(self) -> dict:
        namespaces = self.config.get('namespaces', None)
        
        if not namespaces:
            logging.error("No namespaces in config")
            return {}
        
        return namespaces
    
    @property
    def target(self) -> Path:
        target = self.config.get('target', DEFAULT_TARGET)
        
        if target == DEFAULT_TARGET:
            logging.warning(f"No target directory set, assuming {target}")
            
        return Path(target)
    
    @property
    def reindex(self) -> bool:
        reindex = self.config.get('reindex', DEFAULT_REINDEX)
        
        if not isinstance(reindex, bool):
            logging.error(f"Reindex is not a boolean, assuming {DEFAULT_REINDEX}")
            
            reindex = DEFAULT_REINDEX
            
        return reindex
    
    @property
    def verbose(self):
        return self.config.get('verbose', DEFAULT_VERBOSITY)
    
    @property
    def content_dir(self) -> str:
        return self.config.get('content_dir', DEFAULT_CONTENT_DIR)

    @property
    def media_dir(self) -> str:
        return self.config.get('media_dir', DEFAULT_MEDIA_DIR)

    @property
    def pages_dir(self) -> str:
        return self.config.get('pages_dir', DEFAULT_PAGES_DIR)
    
    @property
    def broken_css(self) -> str:
        return self.config.get('broken_css', DEFAULT_BROKEN_CSS)
    
    @property
    def tags_css(self) -> str:
        return self.config.get('tags_css', DEFAULT_TAGS_CSS)
    
    @property
    def custom_css(self) -> str:
        return self.config.get('custom_css', DEFAULT_CUSTOM_CSS)
    
    @property
    def search_fields(self) -> str:
        return self.config.get('search_fields', DEFAULT_SEARCH_FIELDS)

    @property
    def search_prefix(self) -> str:
        return self.config.get('search_prefix', DEFAULT_SEARCH_PREFIX)

    # TODO should be named search_index
    @property
    def search_file(self) -> str:
        return self.config.get('search_file', DEFAULT_SEARCH_FILE)
    
    @property
    def noise_words(self) -> list[str]:
        
        if 'noise_words' not in self.config:
            return DEFAULT_NOISE_WORDS
        
        noise_words = self.config.get('noise_words', None)
        
        if noise_words:
            return read_noise_words(Path(noise_words))

        return []

class NamespaceConfig:
    
    
    def __init__(self, name, config, wiki):
        # config is a WikiConfig object
        
        self.name = name.lower()
        
        self.wiki_config = wiki.config
        
        self.config = config
    
    @property
    def is_root(self) -> bool:
        return self.config.get('is_root', False)
    
    @property
    def alias(self) -> str:
        return self.config.get('alias', self.name)
    
    @property
    def content(self) -> Path:
        content = self.config.get('content', None)
        
        if content:
            return Path(content)
        
        return Path(self.wiki_config.content_dir) / self.name / self.wiki_config.pages_dir
        
        # return self.config.get('content', f"{self.wiki_config.content_dir}/{self.name}/{self.wiki_config.pages_dir}")
    
    @property
    def target(self) -> Path:
        # target is always relative to wiki target
        return Path(self.wiki_config.target) / self.name
        # return os.path.join(self.wiki_config.target, self.name)
    
    @property
    def broken_css(self) -> str:
        return self.config.get('broken_css', self.wiki_config.broken_css)
    
    @property
    def tags_css(self) -> str:
        return self.config.get('tags_css', self.wiki_config.tags_css)
    
    @property
    def custom_css(self) -> str:
        return self.config.get('custom_css', self.wiki_config.custom_css)
    
    @property
    def search_fields(self) -> str:
        return self.config.get('search_fields', self.wiki_config.search_fields)

    @property
    def search_prefix(self) -> str:
        return self.config.get('search_prefix', self.wiki_config.search_prefix)

    @property
    def search_file(self) -> str:
        return self.config.get('search_file', self.wiki_config.search_file)
    
    @property
    def meta_fields(self) -> list[str]:
        # meta fields are not set at wiki level
        meta_fields = self.config.get('meta_fields', False)

        if meta_fields:
            return [f.strip() for f in meta_fields.split(',')]
        
        return meta_fields
    
    @property
    def noise_words(self) -> str:
        # if no noise_words specified for NS, use Wiki's
        if 'noise_words' not in self.config.keys():
            return self.wiki_config.noise_words
        
        # TODO check noise word files in wiki and NS
        noise_words = self.config.get('noise_words', None)
        
        # if noise_words exists in config but is blank, return empty list
        if not noise_words:
            return []
        
        if isinstance(noise_words, list):
            return noise_words
        
        return read_noise_words(self.content / noise_words)
        
    @property
    def noise_tags(self) -> list[str]:
        return self.config.get('noise_tags', None)


def read_noise_words(path:Path) -> list[str]:
    """Read a file of noise words This file
    should be a plain text file with one word per line.
    
    Args:
        path (str): Path to file, relative to content
    
    Returns:
        list: List of noise words.
    """
    
    # noise words in config is a list or a str (i.e. file). if NS specifies blank then 
    # do not use for that NS
    
    try:
        with path.open('r', encoding='utf-8') as nf:
            noise_words = nf.read()
    except IOError:
        logging.error(f"could not open noise word file '{path}'")
        return []
    
    return noise_words.split('\n')
