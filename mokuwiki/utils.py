"""_summary_
"""
import re
import argparse
import logging

MARKDOWN_PARA_SEP = "\n\n"


class OptionsParser:
    # TODO when these error they report they are mokuwiki, not something else!
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser(exit_on_error=False)
    
    """ See this https://stackoverflow.com/questions/5943249/python-argparse-and-controlling-overriding-the-exit-status-code
    because exit_on_error has bugs
    
    or just do parse_known_args() and ignore errors?
    """
    
    def parse(self, line) -> dict:
        try:
            options = self._parser.parse_args(re.findall(r"(?:\".*?\"|\S)+", line))
        except (argparse.ArgumentError, argparse.ArgumentTypeError):
            logging.error(f"Error parsing directive for {line}")
            # TODO check returned value when used as options.format will not exist etc
            return {}

        # double quotes will have been preserved and must be removed        
        for attr in vars(options):
            if isinstance(getattr(options, attr), str):
                setattr(options, attr, getattr(options, attr).replace('"', '').replace('\\n', '\n'))
        
        return options

class FileIncludeParser(OptionsParser):
    
    def __init__(self) -> None:
        super().__init__()
        self._parser.add_argument('files')
        self._parser.add_argument('--sort', action='store_true', default=True)
        self._parser.add_argument('--sep', default='')
        self._parser.add_argument('--shift', default=0, type=int)
        self._parser.add_argument('--indent', default='')
        self._parser.add_argument('--before', default='\n')
        self._parser.add_argument('--after', default='\n')
        self._parser.add_argument('--header', default='')
        self._parser.add_argument('--format', default='')
        self._parser.add_argument('--repeat', default=1, type=int)
        
        logging.debug("FileIncludeParser initialized")


class ImageIncludeParser(OptionsParser):
    
    def __init__(self) -> None:
        super().__init__()
        self._parser.add_argument('image', nargs='+')
        self._parser.add_argument('--ext', default='jpg')
        self._parser.add_argument('--link', default='')
        self._parser.add_argument('--style', default='')
        self._parser.add_argument('--media', default='')
        self._parser.add_argument('--figure', action='store_true', default=True)
        
        logging.debug("ImageIncludeParser initialized")


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
        
        """TODO --table option eg. --table "<Name:title,Rank:level"
        so would have column_title:metadata_element, then maybe some 
        way of indicating justification and relative width (so start with
        "<" for left, ">" for right and nothing for centered). Plus something
        for making the column wide, e.g. number of + signs after (each one adds len(name) in spaces)
        
        so --table would set --header, --format and --after accordingly
        
        would do this here
        
        """
        
        logging.debug("TagListParser initialized")


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

def make_markdown_span(span_text: str, css_class: str = '') -> str:
    # CHECK can we have empty css for spans? what to do if blank
    if css_class:
        if css_class.startswith('.'):
            css_class = f"{{{css_class}}}"
        else:
            css_class = f"{{.{css_class}}}"
    
    return f"[{span_text}]{css_class}"

def make_markdown_link(show_name: str, page_name: str = '', ns_path: str = '', root_ns: bool = False, anchor_name: str = '') -> str:

    # TODO if namespace targets could be different then you would need to factor that in here
    if not page_name:
        page_name = make_file_name(show_name)

    if anchor_name:
        anchor_name = f"#{anchor_name}"

    if not ns_path:
        # source and target NS are the same
        return f'[{show_name}]({page_name}.html{anchor_name})'

    if root_ns:
        # if target is root just go up one level
        return f'[{show_name}](../{page_name}.html{anchor_name})'
    
    # otherwise go up and come back down
    return f'[{show_name}](../{ns_path}/{page_name}.html{anchor_name})'

def make_wiki_link(title: str, namespace: str = ''):
    """Make a wiki link from a title and optional namespace alias"""
    if title.startswith('[[') and title.endswith(']]'):
        return title
    
    if namespace:
        title = f"{namespace}:{title}"
        
    return f"[[{title}]]"

def make_image_link(image_name: str, caption_name:str|None = None,image_ext: str = 'jpg', media_dir: str = '') -> str:
    
    # TODO with optional class(es)
    
    file_name = make_file_name(image_name, image_ext)

    if not caption_name:
        caption_name = image_name
            
    if media_dir:
        return f'![{caption_name}]({media_dir}/{file_name})'

    return f'![{caption_name}]({file_name})'
