import logging
import yaml

from copy import deepcopy
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mokuwiki.wiki import Wiki


DEFAULT_WIKINAME = 'Wiki'
DEFAULT_TARGET = 'build'
DEFAULT_VERBOSE = 1
DEFAULT_CLEAN = 'never'
DEFAULT_BROKEN_CSS = '.broken'
DEFAULT_TAGS_CSS = '.tag'
DEFAULT_CUSTOM_CSS = '.smallcaps'
DEFAULT_CONTENT_DIR = 'content'
DEFAULT_SITE_DIR = 'site'
DEFAULT_BUILD_DIR = 'build'
DEFAULT_MEDIA_DIR = 'images'
DEFAULT_TOC_LEVEL = 0
DEFAULT_META_HOME = "home"
DEFAULT_META_PREV = "prev"
DEFAULT_META_NEXT = "next"
DEFAULT_META_LINKS = [DEFAULT_META_HOME, DEFAULT_META_NEXT, DEFAULT_META_PREV]
DEFAULT_META_LINKS_BROKEN = False
DEFAULT_SEARCH_FIELDS = ['title', 'alias', 'tags', 'summary', 'keywords']
DEFAULT_SEARCH_PREFIX = ''
DEFAULT_SEARCH_FILE = '_index.json'

DEFAULT_NOISE_WORDS = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for',
                       'if', 'i', 'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on',
                       'or', 'such', 'that', 'the', 'their', 'then', 'there', 'these',
                       'they', 'this', 'to', 'was', 'will', 'with']


class WikiConfig:
    
    def __init__(self, config: dict | str) -> None:
        
        if isinstance(config, dict):
            self.config = config
        elif isinstance(config, str):
            with Path(config).open('r') as cf:
                try:
                    self.config = yaml.safe_load(cf)
                except yaml.YAMLError:
                    # might occur for duplicated namespace names
                    raise ValueError(f"Error reading config file {config}")
        else:
            raise ValueError(f"Bad configuration {config}")
    
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
    
    def asdict(self):
        """Return a dictionary of attributes/properties.
        Used for template substitution. Not all properties
        are included.
        """
    
        return {'wikiname': self.name,
                'site_dir': self.site_dir,
                'build_dir': self.build_dir,
                'media_dir': self.media_dir,
                'broken_css': self.broken_css,
                'tags_css': self.tags_css,
                'custom_css': self.custom_css
                }
    
    @property
    def verbose(self) -> int:
        return self.config.get('verbose', DEFAULT_VERBOSE)

    @property
    def clean(self) -> bool:
        clean = self.config.get('clean', DEFAULT_CLEAN)
        
        if clean not in ['never', 'setup', 'teardown', 'always']:
            clean = 'never'
            
        return clean

    # TODO need to expand user or ~ ... should we add 'home' to asdict()??

    # TODO need to check these exist!!!
    @property
    def site_dir(self) -> Path:
        return Path(self.config.get('site_dir', DEFAULT_SITE_DIR)).expanduser()
    
    @property
    def build_dir(self) -> Path:
        return Path(self.config.get('build_dir', DEFAULT_BUILD_DIR))

    @property
    def media_dir(self) -> str:
        return self.config.get('media_dir', DEFAULT_MEDIA_DIR)
    
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
    def preprocessing(self) -> str:
        # default pre-processing is null
        return self.config.get('preprocessing', [])

    @property
    def postprocessing(self) -> str:
        # default post-processing is null
        return self.config.get('postprocessing', [])
    
    @property
    def templates(self) -> dict:
        return self.config.get('templates', {})

    @property
    def meta_links(self) -> list[str]:
        return DEFAULT_META_LINKS + self.config.get('meta_links', [])
    
    @property
    def meta_links_broken(self) -> bool:
        return self.config.get('meta_links_broken', DEFAULT_META_LINKS_BROKEN)
    
    @property
    def noise_words(self) -> list[str]:
        
        if 'noise_words' not in self.config:
            return DEFAULT_NOISE_WORDS
        
        noise_words = self.config.get('noise_words', None)
        
        if noise_words:
            return read_noise_words(Path(noise_words))

        return []

class NamespaceConfig:
    
    # TODO some kind of "exclude" list to filter out folders, file exts from copying?
    
    def __init__(self, name, config: dict, wiki: 'Wiki') -> None:
        # config is a WikiConfig object
        
        self.name = name.lower()
        
        self.wiki_config = wiki.config
        
        self.config = config
        
        # namespace is for the end folder
        self.namespace = self.name if not self.is_root else ''
    
    def asdict(self):
        """Return a dictionary of attributes/properties.
        Used for template substitution. Not all properties
        are included.
        """
    
        return {'name': self.name,
                'namespace': self.namespace,
                'wikiname': self.wiki_config.name,
                'alias': self.alias,
                'is_root': self.is_root,
                'site_dir': self.wiki_config.site_dir,
                'build_dir': self.build_dir,
                'media_dir': self.media_dir,
                'target_dir': self.target_dir,
                'broken_css': self.broken_css,
                'tags_css': self.tags_css,
                'custom_css': self.custom_css
                }
    
    @property
    def is_root(self) -> bool:
        return self.config.get('is_root', False)
    
    @property
    def alias(self) -> str:
        return self.config.get('alias', self.name)
    
    @property
    def build_dir(self) -> Path:
        """This is the base build dir for all the processes, including the "internal" MW process.
        By default this is the namespace's sub-folder of the wiki build_dir.
        """
        build_dir = self.config.get('build_dir', None)
        
        if build_dir:
            return build_dir
        
        return self.wiki_config.build_dir / self.name
    
    @property
    def content_dirs(self) -> list[Path]:
        """content_dirs are Path objects so use this as base for all NS operations
        """
        content = self.config.get('content', None)
        
        if isinstance(content, str):
            return [Path(Template(content).substitute(self.asdict()))]
        
        if isinstance(content, list):
            return [Path(Template(c).substitute(self.asdict())) for c in content]
        
        logging.error(f"No content defined for namespace {self.name}")
    
    @property
    def media_dir(self) -> str:
        return self.config.get('media_dir', self.wiki_config.media_dir)
    
    @property
    def target_dir(self) -> Path:
        """This is where the internal process has to send the wikified MD files for processing by pandoc
        By default this will be ./build/$NS/mokuwiki, as 'mokuwiki' represents the internal process"""
        return self.config.get('target_dir', self.build_dir / "mokuwiki")
    
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
    def toc(self) -> int:
        toc = self.config.get('toc', DEFAULT_TOC_LEVEL)
        
        try:
            return int(toc)
        except TypeError:
            logging.warning(f"Invalid value for 'toc' ({toc}), assuming {DEFAULT_TOC_LEVEL}")
            
        return DEFAULT_TOC_LEVEL
    
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
    def templates(self) -> dict:
        return self.config.get('templates', self.wiki_config.templates)
    
    @property
    def meta_links(self) -> list[str]:
        """NOTE: meta_links must be a list in the original config
        """
        meta_links = self.config.get('meta_links', [])
        
        if meta_links:
            return DEFAULT_META_LINKS + meta_links
        else:
            return self.wiki_config.meta_links
    
    @property
    def meta_links_broken(self) -> bool:
        return self.config.get('meta_links_broken', self.wiki_config.meta_links_broken)
    
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
        
        # otherwise, if a string assume it refers to a file path
        return read_noise_words(Path(noise_words))
        
    @property
    def noise_tags(self) -> list[str]:
        return self.config.get('noise_tags', None)

    @property
    def preprocessing(self) -> list:

        default = deepcopy(self.wiki_config.preprocessing)
        
        preprocessors: list = self.config.get('preprocessing', [])
        
        default.extend(preprocessors)

        return param_substitution(default, self.asdict())

    @property
    def postprocessing(self) -> list:
        
        default = deepcopy(self.wiki_config.postprocessing)
        
        postprocessors: list = self.config.get('postprocessing', [])
        
        default.extend(postprocessors)

        return param_substitution(default, self.asdict())


def param_substitution(processors: list, params: dict) -> list:
    
    if not isinstance(processors, list):
        logging.error("processes must be a list")
        return []
    
    for i, processor in enumerate(processors):
        
        if isinstance(processor, str):
            processors[i] = Template(processor).substitute(params)
            continue
        
        for _, config in processor.items():
        
            for arg, val in config.items():
            
                if isinstance(val, str):
                    config[arg] = Template(val).substitute(params)
                    continue
            
                if isinstance(val, list):
                    config[arg] = [Template(v).substitute(params) for v in val]
                    continue
            
                if isinstance(val, dict):
                    for k, v in val.items():
                        val[k] = Template(v).substitute(params)
    
    return processors

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
