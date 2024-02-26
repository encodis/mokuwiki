import yaml
from pathlib import Path

from mokuwiki.wiki import Wiki

from utils import Markdown


def test_namespace_nav(tmp_path):
    
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
                   prev: Page One
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
                   prev: Page Two
                   ...
                   Text 3
                   """)

    wiki_config = f"""
        name: test
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
              toc: 1
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()    
    
    actual1 = Path(target) / 'ns1' / 'page_one.md'    
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
    
    actual2 = Path(target) / 'ns1' / 'page_two.md'    
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
    
    actual3 = Path(target) / 'ns1' / 'page_three.md'    
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