import os
from pathlib import Path
import yaml

from mokuwiki.wiki import Wiki

from utils import Markdown


def test_page_links(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   A link to [[Page One]]
                   """)

    wiki_config = f"""
        name: test
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    actual1 = Path(target) / 'ns1' / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    ...
    A link to [Page Two](page_two.html)
    """
    
    assert Markdown.compare(expect1, actual1)

    actual2 = Path(target) / 'ns1' / 'page_two.md'    
    assert actual2.exists()
    
    expect2 = """
    ---
    title: Page Two
    ...
    A link to [Page One](page_one.html)
    """
    
    assert Markdown.compare(expect2, actual2)

def test_page_links_alias(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   A link to [[2nd Page]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   alias: 2nd Page
                   ...
                   A link to [[Page One]]
                   """)

    wiki_config = f"""
        name: test
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    actual1 = Path(target) / 'ns1' / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    ...
    A link to [2nd Page](page_two.html)
    """
    
    assert Markdown.compare(expect1, actual1)

    actual2 = Path(target) / 'ns1' / 'page_two.md'    
    assert actual2.exists()
    
    expect2 = """
    ---
    title: Page Two
    alias: 2nd Page
    ...
    A link to [Page One](page_one.html)
    """
    
    assert Markdown.compare(expect2, actual2)

def test_page_links_display(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   A link to [[P2|Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   A link to [[Page One]]
                   """)

    wiki_config = f"""
        name: test
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    actual1 = Path(target) / 'ns1' / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    ...
    A link to [P2](page_two.html)
    """
    
    assert Markdown.compare(expect1, actual1)

    actual2 = Path(target) / 'ns1' / 'page_two.md'    
    assert actual2.exists()
    
    expect2 = """
    ---
    title: Page Two
    ...
    A link to [Page One](page_one.html)
    """
    
    assert Markdown.compare(expect2, actual2)   

def test_page_links_broken(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   A link to [[Page Two]]
                   """)

    wiki_config = f"""
        name: test
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    actual1 = Path(target) / 'ns1' / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    ...
    A link to [Page Two]{.broken}
    """
    
    assert Markdown.compare(expect1, actual1)

# TODO alternate CSS for broken link ?


def test_page_links_metadata_string(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   subtitle: Page Two
                   ...
                   Text 1
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
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
              meta_fields: ['subtitle']
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    actual1 = Path(target) / 'ns1' / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    subtitle: '[Page Two](page_two.html)'
    ...
    Text 1
    """
    
    assert Markdown.compare(expect1, actual1)

def test_page_links_metadata_list(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   tags: [Page Two, Page Three]
                   ...
                   Text 1
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   ...
                   Text 3
                   """)

    wiki_config = f"""
        name: test
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
              meta_fields: ['tags']
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    actual1 = Path(target) / 'ns1' / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    tags: ['[Page Two](page_two.html)', '[Page Three](page_three.html)']
    ...
    Text 1
    """
    
    assert Markdown.compare(expect1, actual1)
    
    
    
    
    
    
    # source_dir = tmpdir.mkdir('source')
    # source_dir.mkdir('ns1')
    # target_dir = tmpdir.mkdir('target')

    # create_markdown_file(source_dir.join('ns1', 'file1.md'),
    #                      {'title': 'Page One',
    #                       'tags': '[Page Two, Page Three]'},
    #                      'Text')

    # create_markdown_file(source_dir.join('ns1', 'file2.md'),
    #                      {'title': 'Page Two'},
    #                      'Text')

    # create_markdown_file(source_dir.join('ns1', 'file3.md'),
    #                      {'title': 'Page Three'},
    #                      'Text')

    # create_wiki_config(str(source_dir.join('test.cfg')),
    #                    None,
    #                    {'name': 'ns1',
    #                     'path': f'{source_dir.join("ns1")}',
    #                     'target': str(target_dir),
    #                     'meta_fields': 'tags'})

    # wiki = Wiki(source_dir.join('test.cfg'))

    # wiki.process_namespaces()

    # assert len(wiki) == 1
    # assert len(wiki.namespaces['ns1']) == 3

    # expect1 = create_markdown_string({'title': 'Page One',
    #                                   'tags': ['[Page Two](page_two.html)', '[Page Three](page_three.html)']},
    #                                  'Text')

    # assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    # with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
    #     actual1 = fh.read()

    # assert compare_markdown_content(expect1, actual1)
