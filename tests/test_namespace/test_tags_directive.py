import yaml
from pathlib import Path

from mokuwiki.wiki import Wiki


from utils import Markdown


def test_process_tags_directive(tmp_path):
    """Test that the directive '{{tag}}' produces a list of pages with that tag,
    and that pages without those tags are not included in the list
    """
   
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
                   ...
                   {{abc}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   {{xyz}}
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
    tags: [abc]
    ...
    [Page One](page_one.html)

    [Page Two](page_two.html)
    """
    
    assert Markdown.compare(expect1, actual1)
    
    actual3 = Path(target) / 'ns1' / 'page_three.md'
    assert actual3.exists()
    
    expect3 = """
    ---
    title: Page Three
    tags: [xyz]
    ...
    [Page Three](page_three.html)
    """
    
    assert Markdown.compare(expect3, actual3)

def test_process_tags_directive_or(tmp_path):
    """Test OR
    """
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
                   ...
                   {{abc def}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   {{xyz}}
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
    tags: [abc]
    ...
    [Page One](page_one.html)

    [Page Two](page_two.html)
    """
    
    assert Markdown.compare(expect1, actual1)
    
    actual3 = Path(target) / 'ns1' / 'page_three.md'
    assert actual3.exists()
    
    expect3 = """
    ---
    title: Page Three
    tags: [xyz]
    ...
    [Page Three](page_three.html)
    """
    
    assert Markdown.compare(expect3, actual3)

def test_process_tags_directive_and(tmp_path):
    """Test AND
    """

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
                   ...
                   {{abc +def}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc, def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   {{xyz}}
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
    
    # only page two has both tags abc and def
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    [Page Two](page_two.html)
    """
    
    assert Markdown.compare(expect1, actual1)
    
    actual3 = Path(target) / 'ns1' / 'page_three.md'
    assert actual3.exists()
    
    expect3 = """
    ---
    title: Page Three
    tags: [xyz]
    ...
    [Page Three](page_three.html)
    """
    
    assert Markdown.compare(expect3, actual3)

def test_process_tags_directive_and_three(tmp_path):
    """Test AND
    """

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
                   ...
                   {{abc +def +ghi}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc, def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   {{xyz}}
                   """)

    file4 = ns1 / 'file4.md'
    Markdown.write(file4,
                   """
                   ---
                   title: Page Four
                   tags: [abc, def, ghi]
                   ...
                   Text Four
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
    
    # only page four has all tags abc, def and ghi
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    [Page Four](page_four.html)
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_tags_directive_not(tmp_path):
    """Test NOT
    """

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
                   ...
                   {{abc -def}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc, def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   {{xyz}}
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
    
    # only page four has all tags abc, def and ghi
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    [Page One](page_one.html)
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_tags_directive_not_and(tmp_path):
    """Test NOT
    """

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
                   ...
                   {{abc +def -ghi}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc, def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [abc, def, ghi, jkl]
                   ...
                   Text 3
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
    
    # only page two has tags abc and def but not ghi
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    [Page Two](page_two.html)
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_tags_directive_list_all(tmp_path):
    """Test LIST ALL
    """

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
                   ...
                   {{*}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc, def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [abc, def, ghi, jkl]
                   ...
                   Text 3
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
    
    # all pages in alphabetical order
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    [Page One](page_one.html)
    
    [Page Three](page_three.html)

    [Page Two](page_two.html)
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_tags_directive_count_all(tmp_path):
    """Test COUNT ALL
    """

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
                   ...
                   {{#}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   Text 3
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
    
    # all pages in alphabetical order
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    3
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_tags_directive_count_tag(tmp_path):
    """Test COUNT TAG
    """

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
                   ...
                   {{#abc}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc, def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   Text 3
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
    
    # all pages in alphabetical order
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    2
    """
    
    assert Markdown.compare(expect1, actual1)

def test_process_tags_directive_list_tags(tmp_path):
    """Test LIST TAGS
    """

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
                   ...
                   {{@}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc, def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   Text 3
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
    
    # all pages in alphabetical order
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    [abc]{.tag}

    [def]{.tag}

    [xyz]{.tag}"""
    
    assert Markdown.compare(expect1, actual1)

def test_process_tags_directive_noise(tmp_path):
    """Test LIST TAGS
    """

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
                   ...
                   {{@}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc, def]
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   ...
                   Text 3
                   """)
    
    wiki_config = f"""
        name: test
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
              noise_tags: [xyz]
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    actual1 = Path(target) / 'ns1' / 'page_one.md'    
    assert actual1.exists()
    
    # all pages in alphabetical order
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    ...
    [abc]{.tag}

    [def]{.tag}"""
    
    assert Markdown.compare(expect1, actual1)
