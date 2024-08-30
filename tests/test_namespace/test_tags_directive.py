import yaml
from pathlib import Path

from mokuwiki.wiki import Wiki


from utils import Markdown


def test_tags_directive(tmp_path):
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
                   tags: [ABC]
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
    
def test_tags_directive_spaces(tmp_path):
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
                   tags: [a bc]
                   ...
                   {{a_bc}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [a bc]
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
    tags: [a bc]
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

def test_tags_directive_multi(tmp_path):
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
                   
                   {{xyz}}
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
    
    
    
    [Page Three](page_three.html)
    """
    
    assert Markdown.compare(expect1, actual1)
    
def test_tags_directive_or(tmp_path):
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

def test_tags_directive_and(tmp_path):
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
                   {{abc &def}}
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

def test_tags_directive_and_three(tmp_path):
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
                   {{abc &def &ghi}}
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

def test_tags_directive_not(tmp_path):
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
                   {{abc !def}}
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

def test_tags_directive_not_and(tmp_path):
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
                   {{abc &def !ghi !xyz}}
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

def test_tags_directive_list_all(tmp_path):
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

def test_tags_directive_count_all(tmp_path):
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

def test_tags_directive_count_tag(tmp_path):
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

def test_tags_directive_list_tags(tmp_path):
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

def test_tags_directive_noise(tmp_path):
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

def test_tags_other_namespace(tmp_path):
    # two pages in same namespace, still need a wiki

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns2 = source / 'ns2'
    ns1.mkdir()
    ns2.mkdir()

    target = tmp_path / 'target'
    target.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   tags: ['a1']
                   ...
                   {{ns2:b2}}
                   """)
    
    file2 = ns2 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: ['b2']
                   ...
                   A link to [[ns1:Page One]]
                   """)

    wiki_config = f"""
        name: test
        target: {target}
        namespaces:
          ns1:
              content: {ns1}
          ns2:
              content: {ns2}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    assert len(wiki) == 2
    assert len(wiki.namespaces['ns1']) == 1
    assert len(wiki.namespaces['ns2']) == 1

    expect1 = """
    ---
    title: Page One
    tags: ['a1']
    ...
    [Page Two](../ns2/page_two.html)
    """

    actual1 = Path(target) / 'ns1' / 'page_one.md'
    
    assert actual1.exists()
    assert Markdown.compare(expect1, actual1)

def test_tags_format(tmp_path):
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
                   foo: bar one
                   ...
                   {{abc --format "X ?{foo} X"}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   foo: bar two
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   foo: bar three
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
    foo: bar one
    ...
    X bar one X
    
    X bar two X
    
    """
    
    assert Markdown.compare(expect1, actual1)

def test_tags_format_template(tmp_path):
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
                   foo: bar one
                   ...
                   {{abc --format foobar}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   foo: bar two
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [xyz]
                   foo: bar three
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

    wiki_config = wiki_config + """
        templates:
          foobar: "X ?{foo} X"
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_namespaces()

    actual1 = Path(target) / 'ns1' / 'page_one.md'    
    assert actual1.exists()
    
    expect1 = """
    ---
    title: Page One
    tags: [abc]
    foo: bar one
    ...
    X bar one X
    
    X bar two X
    
    """
    
    assert Markdown.compare(expect1, actual1)

def test_tags_format_table(tmp_path):
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
                   foo: Text 1
                   bar: 23
                   ...
                   {{abc --format "| ?{foo} | ?{bar} |" --after "" --header "| Foo | Bar |\\n|-----|-----|"}}
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   foo: Text 2
                   bar: 67.4
                   ...
                   Text 2
                   """)

    file3 = ns1 / 'file3.md'
    Markdown.write(file3,
                   """
                   ---
                   title: Page Three
                   tags: [abc]
                   foo: Text 3
                   bar: 92
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
    foo: Text 1
    bar: 23
    ...
    | Foo | Bar |
    |-----|-----|
    | Text 1 | 23 |
    | Text 2 | 67.4 |
    | Text 3 | 92 |
    
    """
    
    assert Markdown.compare(expect1, actual1)

