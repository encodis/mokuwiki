import os

from mokuwiki import mokuwiki


def test_single_file_mode(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
tags: [abc]
...

A line of text.
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
tags: [abc]
...

A line of text.
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual

# TODO add test where two files are given and check error message
