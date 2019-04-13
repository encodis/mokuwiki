import os
import json
import deepdiff

from mokuwiki import mokuwiki


def test_search_index(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

A link to [[Page Two]]
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...

This is Page Two
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, index=True)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, '_index.json'))

    # assert contents of page_one.md have a link to page_two.md
    expect = [
        {
            'file': 'page_one',
            'title': 'Page One',
            'terms': ['abc', 'one', 'page']
        },
        {
            'file': 'page_two',
            'title': 'Page Two',
            'terms': ['two', 'abc', 'page']
        }
    ]

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads('[' + index.split('[', 1)[1])

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_prefix(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

A link to [[Page Two]]
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...

This is Page Two
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, index=True, prefix='')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, '_index.json'))

    # assert contents of page_one.md have a link to page_two.md
    expect = [
        {
            'file': 'page_one',
            'title': 'Page One',
            'terms': ['abc', 'one', 'page']
        },
        {
            'file': 'page_two',
            'title': 'Page Two',
            'terms': ['two', 'abc', 'page']
        }
    ]

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    # with no prefix, just look at JSON
    actual = json.loads(index)

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)


def test_search_index_noindex(tmpdir):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

A link to [[Page Two]]
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
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

    # assert contents of page_one.md have a link to page_two.md
    expect = [
        {
            'file': 'page_one',
            'title': 'Page One',
            'terms': ['abc', 'one', 'page']
        }
    ]

    with open(os.path.join(target_dir, '_index.json'), 'r', encoding='utf8') as fh:
        index = fh.read()

    actual = json.loads('[' + index.split('[', 1)[1])

    # use DeepDiff to compare structures
    assert not deepdiff.DeepDiff(expect, actual, ignore_order=True)
