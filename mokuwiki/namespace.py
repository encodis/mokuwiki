from pathlib import Path
import logging
from typing import TYPE_CHECKING

from mokuwiki.page import Page
from mokuwiki.config import NamespaceConfig
import mokuwiki.index as idx
from mokuwiki.utils import make_markdown_link, make_markdown_span

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

        if not self.config.content_dir or not Path(self.config.content_dir).is_dir():
            logging.warning(f"namespace path '{self.config.content_dir}' does not exist, skipping")
            raise ValueError

        self.is_root = self.config.is_root

        # create target path
        self.config.target_dir.mkdir(parents=True, exist_ok=True)
        
        self.index = idx.Index(self)

        # TODO test support for '**' in glob spec, with recursive=True
        # titles must be unique? or allow path to be multivalued
        # or ensure there is a pre stage that copies the files in the build file, then they would
        # need to be unique

        self.pages = []
        
        for page_path in self.config.content_dir.glob('*.md'):
            # pass in ref to namespace
            try:
                page = Page(page_path, self)
            except ValueError:
                logging.error(f"page '{page_path}' could not be created")
                continue
            
            try:
                self.index.add_page(page)
            except ValueError:
                logging.warning(f"page '{page.title}' or elements already exists in index")
                continue
            
            self.pages.append(page)

        # self.modified = os.path.getmtime(self.config.target)
        self.modified = self.config.target_dir.stat().st_mtime

        logging.info(f"created namespace '{self.name}'")

    def __len__(self) -> int:
        """The 'size' of the namespace is the number of pages.

        Returns:
            int: Number of valid pages in wiki
        """
        return len(self.pages)

    def get_page(self, page_title) -> Page|None:
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
            
        return None

    def generate_stories(self) -> None:
        """basically, just insert next/prev
        
        and return home page
        """
        
        self.home_page = None
        
        # get home page
        for page in self.pages:
            if page.meta.get('home', False):
                if self.home_page:
                    logging.error(f"Ignoring duplicate home page {page.title}")
                else:
                    self.home_page = page
        
        if not self.home_page:
            logging.warning("No home page for story generation")
            return

        self.home_page.meta['home'] = self.home_page.title

        last_page = self.home_page

        for page1 in self.pages:
            
            for page2 in self.pages:
                if not page2.toc_include or page1.title == page2.title:
                    continue
            
                if last_page.meta.get('next', '') == page2.title:
                    page2.meta['prev'] = last_page.title
                    page2.meta['home'] = self.home_page.title
                    last_page = page2
                    break
    
        # TODO return dict of lists of home pages, keyed by title
    
    def generate_story_toc(self) -> None:
        toc_pages = []
        
        toc_pages.append(self.home_page)
        
        current_page = self.home_page
        guard_count = 0
        
        while True:
            next_page = current_page.meta.get('next', False)
            
            # TODO for individual stories use len(story)
            if not next_page or guard_count > len(self):
                break

            guard_count += 1
            
            # get actual page from title
            next_page = self.get_page(next_page)
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
        """i.e. for pages that are not in a story, also obey sort order"""
        pass
        
    def generate_toc(self):
        """Generate ToC
        
        TODO
        - generate stories first
        - then generate story ToCs
        - then get NS ToC from non-story pages
        - then order NS ToC
        """
        
        if self.config.toc == 0:
            return
        
        self.home_page = None
        
        # get home page
        for page in self.pages:
            if page.meta.get('home', False):
                if self.home_page:
                    logging.error(f"Ignoring duplicate home page {page.title}")
                else:
                    self.home_page = page
        
        if not self.home_page:
            logging.warning("No home page for ToC generation")
            return
        
        # set home page for metadata, overwrite boolean value in actual home page
        for page in self.pages:
            page.meta['home'] = make_markdown_link(self.home_page.title)

        # get ordering, starting from home
        toc_pages = []
        
        toc_pages.append(self.home_page)

        last = self.home_page

        for page1 in self.pages:
            
            for page2 in self.pages:
                if not page2.toc_include or page1.title == page2.title:
                    continue
            
                if last.meta.get('next', '') == page2.title:
                    toc_pages.append(page2)
                    page2.meta['prev'] = last.title
                    
                    last = page2
                    break
            
        # format toc with CSS as string, using toc-level for each page
        toc = '\n'.join([make_markdown_span(make_markdown_link(p.title), f"toc{p.toc_level}") for p in toc_pages])
            
        # insert ToC as metadata into each page
        for page in self.pages:
            if not page.toc_display:
                continue
            
            page.meta['ns-toc'] = toc
    
            # CHECK is this done by convert_metadata_links()? No but they could be with suitable defaults
            if 'next' in page.meta:
                page.meta['next'] = make_markdown_link(page.meta['next'])

            if 'prev' in page.meta:
                page.meta['prev'] = make_markdown_link(page.meta['prev'])


    def process_pages(self) -> None:
        """Process each page, first processing any embedded directives,
        then outputting the result to the namespace's target.
        """

        # TODO if stories then ignore config.toc, this is only for ns toc OR is it up to each page to display?
        # so don't need that conf option
        if self.config.toc > 0:
            # TODO gen_stories() returns dict of list, keyed by story home
            self.generate_stories()
            # TODO loop over this to gen each story toc
            self.generate_story_toc()
            
            # TODO then generate NS toc for all pages that DON'T have a story toc (i.e. a home)
            # self.generate_toc()

        for page in self.pages:
            page.process_directives()
            page.save()

        if self.config.search_fields:
            self.index.export_search_index()
