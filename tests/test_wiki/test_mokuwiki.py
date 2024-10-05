
# TODO should test config and namespace overrides etc
# NOTE that most tests have set the default section of test.cfg to default in create_wiki_config()

from pathlib import Path
import yaml

from mokuwiki.wiki import Wiki

from utils import Markdown

PROCESS = 'mokuwiki'


def test_multiple_namespaces(tmp_path):
    # two pages in same namespace, still need a wiki

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns2 = source / 'ns2'
    ns1.mkdir()
    ns2.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   A link to [[ns2:Page Two]]
                   """)
    
    file2 = ns2 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   A link to [[ns1:Page One]]
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

    assert len(wiki) == 2
    assert len(wiki.namespaces['ns1']) == 1
    assert len(wiki.namespaces['ns2']) == 1

    expect1 = """
    ---
    title: Page One
    ...
    A link to [Page Two](../ns2/page_two.html)
    """

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    
    assert actual1.exists()
    assert Markdown.compare(expect1, actual1)

    expect2 = """
    ---
    title: Page Two
    ...
    A link to [Page One](../ns1/page_one.html)
    """
    
    actual2 = tmp_path / 'ns2' / PROCESS / 'page_two.md'
    
    assert actual2.exists()
    assert Markdown.compare(expect2, actual2)


def test_multiple_namespaces_aliases(tmp_path):
    # two pages in same namespace, still need a wiki

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns2 = source / 'ns2'
    ns1.mkdir()
    ns2.mkdir()

    file1 = ns1 / 'file1.md'
    
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   ...
                   A link to [[2nd Page|Y:Page Two]]
                   """)
    
    file2 = ns2 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   A link to [[X:Page One]]
                   """)

    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              alias: X
              content: {ns1}
          ns2:
              alias: Y
              content: {ns2}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    assert len(wiki) == 2
    assert len(wiki.namespaces['ns1']) == 1
    assert len(wiki.namespaces['ns2']) == 1


    expect1 = """
    ---
    title: Page One
    ...
    A link to [2nd Page](../ns2/page_two.html)
    """

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    
    assert actual1.exists()
    assert Markdown.compare(expect1, actual1)

    expect2 = """
    ---
    title: Page Two
    ...
    A link to [Page One](../ns1/page_one.html)
    """
    
    actual2 = tmp_path / 'ns2' / PROCESS / 'page_two.md'
    
    assert actual2.exists()
    assert Markdown.compare(expect2, actual2)
