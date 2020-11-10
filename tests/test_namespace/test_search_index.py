import os
import json
import deepdiff

from mokuwiki import mokuwiki


# helper function to create pages
def make_test_page(title, tags, content=''):
    return f'''---
title: {title}
tags: [{tags}]
...

{content}
'''


def test_search_index(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, index=True)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, '_index.json'))

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

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_prefix(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, index=True, prefix='var MW = MW || {};\nMW.searchIndex = ')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, '_index.json'))

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

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    # assert index starts with prefix
    assert index.startswith('var MW = MW || {};\nMW.searchIndex = ')

    # with no prefix, just look at JSON
    actual = json.loads('{' + index.split('{', 2)[2])

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_noindex(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two'))

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
tags: [abc]
noindex: true
...

This is Page Two
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, index=True)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, '_index.json'))

    # assert contents of index do not contain page two
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

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_noise_words(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc, xyz', 'A link to [[Page Two'))

    file2 = source_dir.join('noise.txt')
    file2.write('''xyz
two''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, index=True, noise=file2)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, '_index.json'))

    # assert index does not contain words in noise list
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

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_fields(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, index=True, fields='title')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, 'page_two.md'))
    assert os.path.exists(os.path.join(target_dir, '_index.json'))

    # assert index only contains words in titles
    expect = {
        "page": [
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

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_content(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc', 'This is Page Two'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, index=True, fields='_body_')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, 'page_two.md'))
    assert os.path.exists(os.path.join(target_dir, '_index.json'))

    # assert index contains only words in body
    expect = {
        "page": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ],
        "link": [
            ["page_one", "Page One"]
        ],
        "two": [
            ["page_one", "Page One"],
            ["page_two", "Page Two"]
        ]
    }

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)

