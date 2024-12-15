from pathlib import Path
import logging
from typing import TYPE_CHECKING

from mokuwiki.page import Page
from mokuwiki.config import NamespaceConfig, DEFAULT_META_HOME, DEFAULT_META_NEXT, DEFAULT_META_PREV, DEFAULT_META_LINKS
import mokuwiki.index as idx
from mokuwiki.process import Processor
from mokuwiki.utils import make_markdown_link, make_markdown_span, make_wiki_link

if TYPE_CHECKING:
    from mokuwiki.wiki import Wiki


class Namespace:
    """The Namespace class definition.

    An instance of a namespace contains the pages in the namespace, their index
    and any namespace related configuration. The namespaces controls the
    creation and processing of all pages (unless a page has been created in
    "single file" mode).
    """

    def __init__(self, name, config: dict, wiki: 'Wiki') -> None:
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

        self.is_root = self.config.is_root

        # create target path (will create namespace build dir too)
        self.config.target_dir.mkdir(parents=True, exist_ok=True)
        
        self.index = idx.Index(self)
        self.processor = Processor()

        # TODO test support for '**' in glob spec, with recursive=True
        # titles must be unique? or allow path to be multivalued
        # or ensure there is a pre stage that copies the files in the build file, then they would
        # need to be unique

        self.pages = []

        # self.modified = os.path.getmtime(self.config.target)
        self.modified = self.config.target_dir.stat().st_mtime

        logging.info(f"created namespace '{self.name}'")

    def __len__(self) -> int:
        """The 'size' of the namespace is the number of pages.

        Returns:
            int: Number of valid pages in wiki
        """
        return len(self.pages)

    def __eq__(self, other) -> bool:
        return True if self.title == other.title else False

    def preprocess_pages(self) -> None:
        self.processor.process(self.config.preprocessing)        
        logging.debug(f"pre-processed namespace '{self.name}'")

    def postprocess_pages(self) -> None:
        self.processor.process(self.config.postprocessing)
        logging.debug(f"post-processed namespace '{self.name}'")

    def load_pages(self) -> None:
        
        for content_dir in self.config.content_dirs:
            
            if not content_dir or not Path(content_dir).is_dir():
                logging.warning(f"namespace path '{content_dir}' does not exist, skipping")
                continue
            
            for page_path in content_dir.glob('*.md'):
                # pass in ref to namespace
                try:
                    page = Page(page_path, self)
                except ValueError:
                    logging.error(f"page '{page_path}' could not be created")
                    continue
                
                # now index page
                try:
                    self.index.add_page(page)
                except ValueError:
                    logging.warning(f"page '{page.title}' or elements already exists in index")
                    continue
                
                self.pages.append(page)

        logging.debug(f"loaded namespace '{self.name}'")

    def get_page(self, page_title) -> Page|None:
        """Get a reference to a page given the page title.
        If no titles match then try aliases.

        Args:
            page_title (str): The page title (case sensitive)
        """
        
        # TODO shouldn't this use self.index ???
        
        for page in self.pages:
            if page.title == page_title:
                return page
            
            if page.alias == page_title:
                return page

        # if still here try aliases
        # TODO this will not be a list, alias is a string
        # for page in page.alias:
        #     if page.alias == page_title:
        #         return page
            
        return None

    def process_pages(self) -> None:
        """Process each page, first processing any embedded directives,
        then outputting the result to the namespace's target.
        """

        # so don't need that conf option
        if self.config.toc > 0:
            self.generate_stories()
            self.generate_story_tocs()
            self.generate_ns_toc()
            self.update_story_links()

        for page in self.pages:
            page.process_directives()
            page.save()

        if self.config.search_fields:
            self.index.export_search_index()

        logging.debug(f"processed namespace '{self.name}'")

    def report_broken_links(self) -> None:
        """Report broken links. If the verbose level is set
        to 3 then report broken links.
        """
        
        for page_name in self.index.get_broken():
            logging.debug(f'broken link: {self.name}:{page_name}')

    def generate_stories(self) -> None:
        """basically, just insert next/prev
        
        and return home page
        
        TODO: may want to use a story prefix for filenames e.g. in rules we would have core-intro.md, eberron-intro.md
        and so on
        
        TODO: could you have a story tag? so you could list all stories? and pages in a story?
        with a special tag prefix {{core %story}} ???
        
        As all HF/content/**/rules/*.m is going into same folder maybe each story does need a string
        that can be used to uniquify a filename, i.e. auto gets added in slugify...
        
        """
        
        # TODO have a "story title" like "Core Rules"
                
        self.home_pages = [p for p in self.pages if p.meta.get(DEFAULT_META_HOME, False)]
        
        if not self.home_pages:
            logging.info("No home pages for story generation")
            return

        for home_page in self.home_pages:

            home_page.meta[DEFAULT_META_HOME] = home_page.title

            last_page = home_page

            for page1 in self.pages:
                
                for page2 in self.pages:
                    if not page2.toc_include or page1.title == page2.title:
                        continue
            
                    if last_page.meta.get(DEFAULT_META_NEXT, '') == page2.title:
                        page2.meta[DEFAULT_META_PREV] = last_page.title
                        page2.meta[DEFAULT_META_HOME] = home_page.title
                        last_page = page2
                        break
        
    def generate_story_tocs(self) -> None:
        """Note that ToC generation just makes the Markdown links explicitly here, so not
        wait until metadata is processed. But the individual meta links are processed then"""
        
        for home_page in self.home_pages:
            
            toc_pages = []
        
            toc_pages.append(home_page)
        
            current_page = home_page
            guard_count = 0
        
            while True:
                logging.debug(f'generating story ToC for: {current_page.title}')

                next_page = current_page.meta.get(DEFAULT_META_NEXT, False)
            
                if not next_page or guard_count > len(self):
                    break

                guard_count += 1
            
                # get actual page from title
                next_page = self.get_page(next_page)
                
                # TODO need to check whether next page exists
                
                toc_pages.append(next_page)            
                current_page = next_page
            
            # format toc with CSS as string, using toc-level for each page
            toc = '\n'.join([make_markdown_span(make_markdown_link(p.title), f"toc{p.toc_level}") for p in toc_pages])
            
            # insert ToC as metadata into each page
            for page in toc_pages:
                if not page.toc_display:
                    continue
            
                page.meta['ns-toc'] = toc
            
    def generate_ns_toc(self) -> None:
        """i.e. for pages that are not in a story, also obey sort order
        Should be run AFTER story ToC generation"""
            
        toc_pages = [p for p in self.pages if not p.meta.get(DEFAULT_META_HOME, False)]
            
        if len(toc_pages) == 0:
            return
        
        # use tuple for nested sort
        toc_pages = sorted(toc_pages, key=lambda p: (p.toc_order, p.title))
    
        toc = '\n'.join([make_markdown_span(make_markdown_link(p.title), f"toc{p.toc_level}") for p in toc_pages])

        for page in toc_pages:
            if not page.toc_display:
                continue
            
            page.meta['ns-toc'] = toc

    def update_story_links(self):
        
        for page in self.pages:
            for nav in DEFAULT_META_LINKS:
                if nav not in page.meta:
                    continue
                page.meta[nav] = make_wiki_link(page.meta[nav])

