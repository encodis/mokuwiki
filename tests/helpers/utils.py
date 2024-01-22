import yaml
from textwrap import dedent
from pathlib import Path
import logging

class Markdown:
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def read(path: Path) -> str:
        with path.open('r', encoding='utf8') as mf:
            content = mf.read()
            
        return Markdown.tidy(content)
    
    @staticmethod
    def write(path: Path, content: str) -> None:
        with path.open('w', encoding='utf8') as mf:
            mf.write(Markdown.tidy(content))
        
    @staticmethod
    def compare(md1, md2, what='both') -> bool:

        if isinstance(md1, str):
            md1 = Markdown.tidy(md1)
        else:
            md1 = Markdown.read(md1)

        if isinstance(md2, str):
            md2 = Markdown.tidy(md2)
        else:
            md2 = Markdown.read(md2)

        meta1, _, body1 = md1.partition('...\n')
        meta2, _, body2 = md2.partition('...\n')

        if what in ['meta', 'both']:
            try:
                meta1 = yaml.safe_load(meta1)
            except yaml.YAMLError:
                logging.error('Error in metadata for content 1')
                return False

            try:
                meta2 = yaml.safe_load(meta2)
            except yaml.YAMLError:
                logging.error('Error in metadata for content 2')
                return False

            if meta1 != meta2:
                return False

        if what in ['body', 'both']:
            body1 = Markdown.trim(body1)
            body2 = Markdown.trim(body2)
        
            if body1 != body2:
                return False

        return True

    @staticmethod
    def tidy(content: str) -> str:
        """Remove any line indents
        """        
        return dedent(content).strip()

    @staticmethod
    def trim(content: str) -> str:
        """Remove all leading and trailing blank lines
        """
        
        content = content.split('\n')
        
        for _ in [1, 2]:
            for _ in content:
                if content[-1] == '':
                    content.pop()
                
            content.reverse()

        return '\n'.join(content)
