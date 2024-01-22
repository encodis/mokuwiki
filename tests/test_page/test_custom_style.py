from mokuwiki.page import Page

from utils import Markdown

def test_process_custom_style(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = source / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   A ^^custom style^^ in a line
                   """)

    page = Page(file1, None)
    page.process_directives()
        
    page.save(target / 'page_one.md')

    actual1 = target / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    ...
    A [custom style]{.smallcaps} in a line
    """
    
    assert Markdown.compare(expect1, actual1)
    

# TODO test a link that has custom styling, but will need two pages in a namespace
