from mokuwiki.page import Page

from utils import Markdown


def test_image_links(tmp_path):
    
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
                   !!An Image!!
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
    ![An Image](images/an_image.jpg)
    """
    
    assert Markdown.compare(expect1, actual1)
    
def test_image_links_format(tmp_path):
    
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
                   !!An Image|png!!
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
    ![An Image](images/an_image.png)
    """
    
    assert Markdown.compare(expect1, actual1)


# TODO test media dir if settable in single file mode
