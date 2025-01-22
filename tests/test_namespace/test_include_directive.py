import os
from pathlib import Path

import yaml

from mokuwiki.wiki import Wiki

from utils import Markdown

PROCESS = 'mokuwiki'


def test_file_includes(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    Included Text
    """
    
    assert Markdown.compare(expect1, actual1)

def test_file_includes_plain(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.txt>>
                   """)
    
    file2 = ns1 / 'file2.txt'
    Markdown.write(file2,
                   """
                   Included Text line 1
                   Included Text line 2
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

    actual1 = tmp_path/ 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    Included Text line 1
    Included Text line 2
    """
    
    assert Markdown.compare(expect1, actual1)

def test_file_includes_plain_folder(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    images = ns1 / 'images'
    images.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<./images/image.map>>
                   """)
    
    file2 = images / 'image.map'
    Markdown.write(file2,
                   """
                   <map name="test">
                   <area/>
                   </map>
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

    actual1 = tmp_path/ 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    <map name="test">
    <area/>
    </map>
    """
    
    assert Markdown.compare(expect1, actual1)

def test_file_includes_globbing(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<fileX*.md --sort>>
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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    Included Two
    
    Included Three
    """
        
    assert Markdown.compare(expect1, actual1)

def test_file_includes_globbing_nosort(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<fileA*.md>>
                   """)
    
    file2 = ns1 / 'fileAB.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   Included Two
                   """)

    file3 = ns1 / 'fileAA.md'
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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    Included Three
    
    Included Two
    """
        
    assert Markdown.compare(expect1, actual1)

def test_file_includes_separator(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
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

def test_file_includes_format(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'fileX1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   foo: Text 1
                   bar: 12
                   ...
                   <<fileX*.md --format "X ?{foo} is ?{bar}">>
                   """)
    
    file2 = ns1 / 'fileX2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   foo: Text 2
                   bar: 36                   
                   ...
                   Included Two
                   """)

    file3 = ns1 / 'fileX3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   foo: Text 3
                   bar: 822
                   ...
                   Included Three
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

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    foo: Text 1
    bar: 12
    ...
    X Text 1 is 12
    
    X Text 2 is 36
    
    X Text 3 is 822
    """
        
    assert Markdown.compare(expect1, actual1)

def test_file_includes_format_template(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'fileX1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   foo: Text 1
                   bar: 12
                   ...
                   <<fileX*.md --format foobar>>
                   """)
    
    file2 = ns1 / 'fileX2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   foo: Text 2
                   bar: 36                   
                   ...
                   Included Two
                   """)

    file3 = ns1 / 'fileX3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   foo: Text 3
                   bar: 822
                   ...
                   Included Three
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki_config = wiki_config + """
        templates:
          foobar: "X ?{foo} is ?{bar}"
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    foo: Text 1
    bar: 12
    ...
    X Text 1 is 12
    
    X Text 2 is 36
    
    X Text 3 is 822
    """
        
    assert Markdown.compare(expect1, actual1)

def test_file_includes_format_table(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'fileX1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   foo: Text 1
                   bar: 12
                   ...
                   <<fileX*.md --format "| ?{foo} | ?{bar} |" --after "" --header "| Foo | Bar |\\n|-----|-----|">>
                   """)
    
    file2 = ns1 / 'fileX2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   foo: Text 2
                   bar: 36                   
                   ...
                   Included Two
                   """)

    file3 = ns1 / 'fileX3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   foo: Text 3
                   bar: 822
                   ...
                   Included Three
                   """)
    
    # TODO test format with metalinks    
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    foo: Text 1
    bar: 12
    ...
    | Foo | Bar |
    |-----|-----|
    | Text 1 | 12 |
    | Text 2 | 36 |
    | Text 3 | 822 | 
    
    """
        
    assert Markdown.compare(expect1, actual1)
    
def test_file_includes_by_namespace(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    ns2 = source / 'ns2'
    ns2.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<"ns2:Page Two">>
                   """)
    
    file2 = ns2 / 'file2.md'
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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
          ns2:
              content: {ns2}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    Included Text
    """
    
    assert Markdown.compare(expect1, actual1)

def test_file_includes_by_namespace_repeat(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    ns2 = source / 'ns2'
    ns2.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<"ns2:Page Two" --repeat 2>>
                   """)
    
    file2 = ns2 / 'file2.md'
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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
          ns2:
              content: {ns2}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    Included Text
    
    Included Text
    """
    
    assert Markdown.compare(expect1, actual1)


def test_file_includes_shift(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.md --shift 1>>
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   # Heading 1
                   
                   Included Text
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

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    ## Heading 1
    
    Included Text
    """
    
    assert Markdown.compare(expect1, actual1)

def test_file_includes_shift_down(tmp_path):
    
    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.md --shift -1>>
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   ### Heading 1
                   
                   Included Text
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

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    ## Heading 1
    
    Included Text
    """
    
    assert Markdown.compare(expect1, actual1)

def test_file_includes_line_indent(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    > Included Text
    """
        
    assert Markdown.compare(expect1, actual1)

def test_file_includes_separator_and_line_indent(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
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

def test_file_includes_prefix_and_suffix(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
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

def test_file_includes_prefix_and_indent(tmp_path):

    # TODO this does not work in production - same reason NS TOC as nested lists did not???

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   f"""
                   ---
                   title: Page One
                   ...
                   <<file2.md --indent "> " --shift 1>>
                   """)

    # note: 'Included Text' is left justifed because the \n in the prefix messes up dedent()
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Three
                   prefix: '### Prefix\n\n'
                   ...
Included Text

More Included Text
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

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    > #### Prefix
    > Included Text
    > 
    > More Included Text
    """
        
    assert Markdown.compare(expect1, actual1)

def test_file_includes_metadata_replace(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    Included page is Page Two
    """
    
    assert Markdown.compare(expect1, actual1)

def test_file_includes_metadata_replace_multi(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

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
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    actual1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert actual1.exists()

    expect1 = """
    ---
    title: Page One
    ...
    Included page is Page Two with subtitle Second Page
    """
    
    assert Markdown.compare(expect1, actual1)
