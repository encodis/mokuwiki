import yaml
from pathlib import Path

from mokuwiki.wiki import Wiki

from utils import Markdown

PROCESS = 'mokuwiki'


def test_namespace_story(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   tags: [abc]
                   toc-include: true
                   toc-level: 1
                   home: true
                   next: Page Two
                   ...
                   Text 1
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   toc-include: true
                   toc-level: 2
                   next: Page Three
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   toc-include: true
                   toc-level: 3
                   prev: Some Other Page
                   ...
                   Text 3
                   """)

    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              toc: 1
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()    
    
    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    home: "[Page One](page_one.html)"
    next: "[Page Two](page_two.html)"
    toc-include: true
    toc-level: 1
    ns-toc: |-
        [[Page One](page_one.html)]{.toc1}
        [[Page Two](page_two.html)]{.toc2}
        [[Page Three](page_three.html)]{.toc3}
    ...
    Text 1
    """
    
    assert Markdown.compare(expect1, actual1)
    
    actual2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'    
    assert actual2.exists()
    
    expect2 = """
    ---
    title: Page Two
    tags: [abc]
    home: "[Page One](page_one.html)"
    prev: "[Page One](page_one.html)"
    next: "[Page Three](page_three.html)"
    toc-include: true
    toc-level: 2
    ns-toc: |-
        [[Page One](page_one.html)]{.toc1}
        [[Page Two](page_two.html)]{.toc2}
        [[Page Three](page_three.html)]{.toc3}
    ...
    Text 2
    """
    
    assert Markdown.compare(expect2, actual2)
    
    actual3 = tmp_path / 'ns1' / PROCESS / 'page_three.md'    
    assert actual3.exists()
    
    expect3 = """
    ---
    title: Page Three
    tags: [xyz]
    home: "[Page One](page_one.html)"
    prev: "[Page Two](page_two.html)"
    toc-include: true
    toc-level: 3
    ns-toc: |-
        [[Page One](page_one.html)]{.toc1}
        [[Page Two](page_two.html)]{.toc2}
        [[Page Three](page_three.html)]{.toc3}
    ...
    Text 3
    """
    
    assert Markdown.compare(expect3, actual3)
    
def test_namespace_multi_stories(tmp_path):
    """Page One starts story one and links to Page Two
       Page Three starts story two and links to Page Four
    """
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   tags: [abc]
                   toc-include: true
                   toc-level: 1
                   home: true
                   next: Page Two
                   ...
                   Text 1
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   toc-include: true
                   toc-level: 2
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   toc-include: true
                   toc-level: 1
                   home: true
                   next: Page Four
                   ...
                   Text 3
                   """)

    file4 = ns1 / 'file4.md'
    Markdown.write(file4,
                   """
                   ---
                   title: Page Four
                   tags: [xyz]
                   toc-include: true
                   toc-level: 2
                   ...
                   Text 4
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              toc: 1
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()    
    
    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    home: "[Page One](page_one.html)"
    next: "[Page Two](page_two.html)"
    toc-include: true
    toc-level: 1
    ns-toc: |-
        [[Page One](page_one.html)]{.toc1}
        [[Page Two](page_two.html)]{.toc2}
    ...
    Text 1
    """
    
    assert Markdown.compare(expect1, actual1)
    
    actual2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'    
    assert actual2.exists()
    
    expect2 = """
    ---
    title: Page Two
    tags: [abc]
    home: "[Page One](page_one.html)"
    prev: "[Page One](page_one.html)"
    toc-include: true
    toc-level: 2
    ns-toc: |-
        [[Page One](page_one.html)]{.toc1}
        [[Page Two](page_two.html)]{.toc2}
    ...
    Text 2
    """
    
    assert Markdown.compare(expect2, actual2)
    
    actual3 = tmp_path / 'ns1' / PROCESS / 'page_three.md'
    assert actual3.exists()
    
    expect3 = """
    ---
    title: Page Three
    tags: [xyz]
    home: "[Page Three](page_three.html)"
    next: "[Page Four](page_four.html)"
    toc-include: true
    toc-level: 1
    ns-toc: |-
        [[Page Three](page_three.html)]{.toc1}
        [[Page Four](page_four.html)]{.toc2}
    ...
    Text 3
    """
    
    assert Markdown.compare(expect3, actual3)

    actual4 = tmp_path / 'ns1' / PROCESS / 'page_four.md'
    assert actual4.exists()
    
    expect4 = """
    ---
    title: Page Four
    tags: [xyz]
    home: "[Page Three](page_three.html)"
    prev: "[Page Three](page_three.html)"
    toc-include: true
    toc-level: 2
    ns-toc: |-
        [[Page Three](page_three.html)]{.toc1}
        [[Page Four](page_four.html)]{.toc2}
    ...
    Text 4
    """
    
    assert Markdown.compare(expect4, actual4)

def test_namespace_ns_toc(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   tags: [abc]
                   toc-include: true
                   toc-level: 1
                   toc-order: 1
                   ...
                   Text 1
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   toc-include: true
                   toc-level: 2
                   toc-order: 2
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   toc-include: true
                   toc-level: 3
                   toc-order: 2
                   ...
                   Text 3
                   """)

    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              toc: 1
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()    
    
    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    toc-include: true
    toc-level: 1
    toc-order: 1
    ns-toc: |-
        [[Page One](page_one.html)]{.toc1}
        [[Page Three](page_three.html)]{.toc3}
        [[Page Two](page_two.html)]{.toc2}
    ...
    Text 1
    """
    
    assert Markdown.compare(expect1, actual1)
    
    actual2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'    
    assert actual2.exists()
    
    expect2 = """
    ---
    title: Page Two
    tags: [abc]
    toc-include: true
    toc-level: 2
    toc-order: 2
    ns-toc: |-
        [[Page One](page_one.html)]{.toc1}
        [[Page Three](page_three.html)]{.toc3}
        [[Page Two](page_two.html)]{.toc2}
    ...
    Text 2
    """
    
    assert Markdown.compare(expect2, actual2)
    
    actual3 = tmp_path / 'ns1' / PROCESS / 'page_three.md'    
    assert actual3.exists()
    
    expect3 = """
    ---
    title: Page Three
    tags: [xyz]
    toc-include: true
    toc-level: 3
    toc-order: 2
    ns-toc: |-
        [[Page One](page_one.html)]{.toc1}
        [[Page Three](page_three.html)]{.toc3}
        [[Page Two](page_two.html)]{.toc2}
    ...
    Text 3
    """

def test_namespace_story_and_ns_toc():
    pass