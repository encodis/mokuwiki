import os
import json

import deepdiff

from mokuwiki.wiki import Wiki

from utils import create_wiki_config, create_markdown_file


def test_search_index(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc]'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'search_fields': 'title,tags'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))
    assert os.path.exists(target_dir.join('ns1', '_index.json'))

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

    with open(target_dir.join('ns1', '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_prefix(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc]'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'search_fields': 'title,alias,tags,summary,keywords',
                        'search_prefix': 'var MW = MW || {};\nMW.searchIndex = '})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))
    assert os.path.exists(target_dir.join('ns1', '_index.json'))

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

    with open(target_dir.join('ns1', '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    assert index.startswith('var MW = MW || {};\nMW.searchIndex =')

    actual = json.loads('{' + index.split('{', 2)[2])

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_noindex(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc]',
                          'noindex': 'true'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'search_fields': 'title,alias,tags,summary,keywords'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))
    assert os.path.exists(target_dir.join('ns1', '_index.json'))

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

    with open(target_dir.join('ns1', '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_fields(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'alias': 'First Page',
                          'tags': '[abc]'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc]'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'search_fields': 'title,alias,tags'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))
    assert os.path.exists(target_dir.join('ns1', '_index.json'))

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

    with open(target_dir.join('ns1', '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_content(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc]'},
                         'Text')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'search_fields': 'title,tags,_body_'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))
    assert os.path.exists(target_dir.join('ns1', '_index.json'))

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

    with open(target_dir.join('ns1', '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_noise_words_none(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc]'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'search_fields': 'title,tags,_body_',
                        'noise_words': '_'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))
    assert os.path.exists(target_dir.join('ns1', '_index.json'))

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

    with open(target_dir.join('ns1', '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_noise_words_string(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'alias': 'First Apple',
                          'tags': '[abc]'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'alias': 'Second',
                          'tags': '[abc]'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'search_fields': 'title,alias,tags',
                        'noise_words': 'first, apple'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))
    assert os.path.exists(target_dir.join('ns1', '_index.json'))

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
        ],
        "second": [
            ["page_two", "Page Two"]
        ]
    }

    with open(target_dir.join('ns1', '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_noise_file(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'alias': 'First Apple',
                          'tags': '[abc]'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'alias': 'Second',
                          'tags': '[abc]'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'search_fields': 'title,alias,tags',
                        'noise_words': f'file:{source_dir.join("noise.txt")}'})

    nf = source_dir.join('noise.txt')
    nf.write('first\napple\n')

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))
    assert os.path.exists(target_dir.join('ns1', '_index.json'))

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
        ],
        "second": [
            ["page_two", "Page Two"]
        ]
    }

    with open(target_dir.join('ns1', '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)
