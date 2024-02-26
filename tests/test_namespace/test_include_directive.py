import os
from pathlib import Path

import yaml

from mokuwiki.wiki import Wiki

from utils import Markdown


def test_process_file_includes(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.md>>
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   Included Text
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
    Included Text
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_file_includes_globbing(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<fileX*.md>>
                   """)
    
    file2 = ns1 / 'fileX2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   Included Two
                   """)

    file3 = ns1 / 'fileX3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [abc]
                   ...
                   Included Three
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
    Included Two
    
    Included Three
    """
        
    assert Markdown.compare(expect1, actual1)

def test_process_file_includes_separator(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<fileX*.md --sep "\\n* * *\\n">>
                   """)
    
    file2 = ns1 / 'fileX2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   Included Two
                   """)

    file3 = ns1 / 'fileX3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [abc]
                   ...
                   Included Three
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
    Included Two
    
    * * *
    
    Included Three
    """
        
    assert Markdown.compare(expect1, actual1)

def test_process_file_includes_different_namespace(tmp_path):
    pass


def test_process_file_includes_line_prefix(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.md --indent "> " >>
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   Included Text
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
    > Included Text
    """
        
    assert Markdown.compare(expect1, actual1)

def test_process_file_includes_separator_and_line_prefix(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<fileX*.md --sep "\\n* * *\\n" --indent "> ">>
                   """)
    
    file2 = ns1 / 'fileX2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   Included Two
                   """)

    file3 = ns1 / 'fileX3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [abc]
                   ...
                   Included Three
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
    > Included Two
    
    * * *
    
    > Included Three
    """
        
    assert Markdown.compare(expect1, actual1)

def test_process_file_includes_prefix_and_suffix(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.md>>
                   """)

    # note: 'Included Text' is left justifed because the \n in the prefix messes up dedent()
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Three
                   prefix: 'The prefix line\n\n'
                   suffix: '\n\nThe suffix line'
                   ...
Included Text
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
    The prefix line
    Included Text
    The suffix line
    """
        
    assert Markdown.compare(expect1, actual1)

def test_process_file_includes_metadata_replace(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.md>>
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   ...
                   Included page is ?{title}
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
    Included page is Page Two
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_file_includes_metadata_replace_multi(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.md>>
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   subtitle: Second Page
                   ...
                   Included page is ?{title} with subtitle ?{subtitle}
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
    Included page is Page Two with subtitle Second Page
    """
    
    assert Markdown.compare(expect1, actual1)
