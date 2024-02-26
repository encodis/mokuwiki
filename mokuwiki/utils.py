"""_summary_
"""
import re
import argparse
import logging

MARKDOWN_PARA_SEP = "\n\n"


class OptionsParser:
    
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser(exit_on_error=False)
    
    def parse(self, line) -> dict:
        try:
            options = vars(self._parser.parse_args(re.findall(r"(?:\".*?\"|\S)+", line)))
        except (argparse.ArgumentError, argparse.ArgumentTypeError):
            logging.error("Error parsing file include directive")
            return {}
        
        # double quotes will have been preserved and must be removed
        options = {k: v.replace('"', '').replace('\\n', '\n') if isinstance(v, str) else v for k, v in options.items()}
        
        return options

class FileIncludeParser(OptionsParser):
    
    def __init__(self) -> None:
        super().__init__()
        self._parser.add_argument('files')
        self._parser.add_argument('--sort', action='store_true', default=True)
        self._parser.add_argument('--sep', default='')
        self._parser.add_argument('--shift', default=0)
        self._parser.add_argument('--indent', default='')
        self._parser.add_argument('--before', default='\n')
        self._parser.add_argument('--after', default='\n')
    
    
class TagListParser(OptionsParser):
    
    def __init__(self) -> None:
        super().__init__()
        self._parser.add_argument('tags', nargs='+')
        self._parser.add_argument('--sort', action='store_true', default=True)
        self._parser.add_argument('--sep', default='')
        self._parser.add_argument('--format', default='')
        self._parser.add_argument('--header', default='')
        self._parser.add_argument('--before', default='\n')
        self._parser.add_argument('--after', default='\n')


def make_file_name(name: str, ext: str = '') -> str:
    """Return a valid filename from a string, optionally including a file
    extension. For what 'valid' means in this context, see
    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    Args:
        name (str): A name (usually a page or image title)
        ext (str): A file extension (without the dot). Default is blank.
    Returns:
        str: A valid filename
    """
    # TODO should this apply to tag cleaning as well?
    name = str(name).strip().replace(' ', '_').lower()
    name = re.sub(r'(?u)[^-\w.]', '', name)
    
    if ext and not ext.startswith('.'):
        ext =f".{ext}"
        
    return name + ext


def make_markdown_span(span_text: str, css_class: str = '', sep: str = '\n') -> str:
    # CHECK can we have empty css for spans?
    if css_class:
        if css_class.startswith('.'):
            css_class = f"{{{css_class}}}"
        else:
            css_class = f"{{.{css_class}}}"
    
    return f"[{span_text}]{css_class}"

def make_markdown_link(show_name: str, page_name: str = '', ns_path: str = '', root_ns: bool = False) -> str:

    # TODO if namespace targets could be different then you would need to factor that in here
    if not page_name:
        page_name = make_file_name(show_name)

    if not ns_path:
        # source and target NS are the same
        return f'[{show_name}]({page_name}.html)'

    if root_ns:
        # if target is root just go up one level
        return f'[{show_name}](../{page_name}.html)'
    
    # otherwise go up and come back down
    return f'[{show_name}](../{ns_path}/{page_name}.html)'

def make_wiki_link(title: str, namespace: str = ''):
    # CHECK may have to check not already has [[ ]]
    if namespace:
        title = f"{namespace}:{title}"
        
    return f"[[{title}]]"

def make_image_link(image_name: str, ext: str = 'jpg', media_dir: str = '') -> str:
    
    file_name = make_file_name(image_name, ext)
    
    if media_dir:
        return f'![{image_name}]({media_dir}/{file_name})'

    return f'![{image_name}]({file_name})'
