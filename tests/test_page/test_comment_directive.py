from mokuwiki.page import Page

from utils import Markdown

# NOTE: these tests can be done in single file mode, as we're just testing page functionality


def test_convert_comment(tmp_path):

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
                   A line of text
                   
                   // A comment
                   
                   Text ending in // a comment
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
    A line of text
    
    
    
    Text ending in 
    """
    
    assert Markdown.compare(expect1, actual1)
