import json
import yaml
from pathlib import Path

import deepdiff

from mokuwiki.wiki import Wiki

from utils import Markdown

PROCESS = 'mokuwiki'


def test_search_index(tmp_path):

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
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   A link to [[Page One]]
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              search_fields: ['title', 'tags']
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    page1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert page1.exists()
    
    page2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'
    assert page2.exists()
    
    index1 = tmp_path / 'ns1' / PROCESS / '_index.json'
    assert index1.exists()
    
    expect = {
        "page": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "abc": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "one": [
            ["page_one", "Page One"]
        ],
        "two": [
            ["page_two", "Page Two"]
        ]
    }

    with index1.open('r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    assert len(actual) > 0

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_prefix(tmp_path):

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
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   A link to [[Page One]]
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              search_fields: ['title', 'tags']
              search_prefix: 'var MW = MW || {{}}; MW.searchIndex = '
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()
    
    page1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert page1.exists()
    
    page2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'
    assert page2.exists()
    
    index1 = tmp_path / 'ns1' / PROCESS / '_index.json'
    assert index1.exists()

    expect = {
        "page": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "abc": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "one": [
            ["page_one", "Page One"]
        ],
        "two": [
            ["page_two", "Page Two"]
        ]
    }

    with index1.open('r', encoding='utf8') as fh:
        index = fh.read()

    assert index.startswith('var MW = MW || {}; MW.searchIndex =')

    actual = json.loads('{' + index.split('{', 2)[2])
     
    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_noindex(tmp_path):

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
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   noindex: true
                   ...
                   A link to [[Page One]]
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              search_fields: ['title', 'tags']
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    page1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert page1.exists()
    
    page2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'
    assert page2.exists()
    
    index1 = tmp_path / 'ns1' / PROCESS / '_index.json'
    assert index1.exists()

    expect = {
        "page": [
            ["page_one", "Page One"]
        ],
        "abc": [
            ["page_one", "Page One"]
        ],
        "one": [
            ["page_one", "Page One"]
        ]
    }

    with index1.open('r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)
     
    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)

def test_search_index_fields(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   alias: 'First Page'
                   tags: [abc]
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   A link to [[Page One]]
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              search_fields: ['title', 'alias', 'tags']
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    page1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert page1.exists()
    
    page2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'
    assert page2.exists()
    
    index1 = tmp_path / 'ns1' / PROCESS / '_index.json'
    assert index1.exists()

    expect = {
        "page": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "first": [
            ["page_one", "Page One"]
        ],
        "abc": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "one": [
            ["page_one", "Page One"]
        ],
        "two": [
            ["page_two", "Page Two"]
        ]
    }

    with index1.open('r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)
     
    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)

def test_search_index_content(tmp_path):

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
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   Text
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              search_fields: ['title', 'tags', '_body_']
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    page1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert page1.exists()
    
    page2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'
    assert page2.exists()
    
    index1 = tmp_path / 'ns1' / PROCESS / '_index.json'
    assert index1.exists()

    expect = {
        "page": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "link": [
            ["page_one", "Page One"]
        ],
        "text": [
            ["page_two", "Page Two"]
        ],
        "abc": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "one": [
            ["page_one", "Page One"]
        ],
        "two": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ]
    }

    with index1.open('r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)
     
    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)

def test_search_index_noise_words_none(tmp_path):

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
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   tags: [abc]
                   ...
                   A link to [[Page One]]
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              search_fields: ['title', 'tags', '_body_']
              noise_words: 
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    page1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert page1.exists()
    
    page2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'
    assert page2.exists()
    
    index1 = tmp_path / 'ns1' / PROCESS / '_index.json'
    assert index1.exists()

    expect = {
        "page": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "abc": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "a": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "link": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "to": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "one": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "two": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ]
    }

    with index1.open('r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)
     
    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)

def test_search_index_noise_words_list(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   alias: First Page
                   tags: [abc]
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   alias: Second Page
                   tags: [abc]
                   ...
                   A link to [[Page One]]
                   """)
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              search_fields: ['title', 'tags', 'alias', '_body_']
              noise_words: ['first', 'link', 'a', 'to']
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    page1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert page1.exists()

    page2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'
    assert page2.exists()
    
    index1 = tmp_path / 'ns1' / PROCESS / '_index.json'
    assert index1.exists()

    expect = {
        "page": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "abc": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "one": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "two": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "second": [
            ["page_two", "Page Two"]
        ]
    }

    with index1.open('r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)

def test_search_index_noise_file(tmp_path):

    source = tmp_path / 'source'
    source.mkdir()
    
    ns1 = source / 'ns1'
    ns1.mkdir()

    file1 = ns1 / 'file1.md'
    Markdown.write(file1,
                   """
                   ---
                   title: Page One
                   alias: First Page
                   tags: [abc]
                   ...
                   A link to [[Page Two]]
                   """)
    
    file2 = ns1 / 'file2.md'
    Markdown.write(file2,
                   """
                   ---
                   title: Page Two
                   alias: Second Page
                   tags: [abc]
                   ...
                   A link to [[Page One]]
                   """)

    noise = source / 'noise.txt'
    noise.write_text('first\nlink\na\nto')
    
    wiki_config = f"""
        name: test
        build_dir: {tmp_path}
        namespaces:
          ns1:
              content: {ns1}
              search_fields: ['title', 'tags', 'alias', '_body_']
              noise_words: {noise}
        """

    wiki = Wiki(yaml.safe_load(wiki_config))
    wiki.process_wiki()

    page1 = tmp_path / 'ns1' / PROCESS / 'page_one.md'
    assert page1.exists()

    page2 = tmp_path / 'ns1' / PROCESS / 'page_two.md'
    assert page2.exists()
    
    index1 = tmp_path / 'ns1' / PROCESS / '_index.json'
    assert index1.exists()

    expect = {
        "page": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "abc": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "one": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "two": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "second": [
            ["page_two", "Page Two"]
        ]
    }

    with index1.open('r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)
