from mokuwiki.page import Page
from mokuwiki.wiki import Wiki
import yaml

from utils import Markdown

PROCESS = 'mokuwiki'

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
    
def test_image_links_ext(tmp_path):
    
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
                   !!An Image --ext png!!
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

def test_image_links_media(tmp_path):
    
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
                   !!An Image --media media!!
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
    ![An Image](media/an_image.jpg)
    """
    
    assert Markdown.compare(expect1, actual1)

def test_image_links_style(tmp_path):
    
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
                   !!An Image --style ".aaa #bbb"!!
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
    ![An Image](images/an_image.jpg){.aaa #bbb}
    """
    
    assert Markdown.compare(expect1, actual1)

def test_image_links_link(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   !!An Image --link "Page Two"!!
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   Text 2
                   """)

    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS /  'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    ...
    <a href='page_two.html'>
    
    ![An Image](images/an_image.jpg)
    
    </a>
    """
    
    assert Markdown.compare(expect1, actual1)

def test_image_links_link_ns(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    ns2 = source / 'ns2'
    ns2.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   !!An Image --link "ns2:Page Two"!!
                   """)
    
    file2 = ns2 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   Text 2
                   """)

    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
          ns2:
              content: {ns2}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS /  'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    ...
    <a href='../ns2/page_two.html'>
    
    ![An Image](images/an_image.jpg)
    
    </a>
    """
    
    assert Markdown.compare(expect1, actual1)

def test_image_links_link_and_style(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   !!An Image --link "Page Two" --style ".aaa #bbb"!!
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   Text 2
                   """)

    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS /  'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    ...
    <a href='page_two.html'>
    
    ![An Image](images/an_image.jpg){.aaa #bbb}
    
    </a>
    """
    
    assert Markdown.compare(expect1, actual1)

# TODO test media dir if settable in single file mode
