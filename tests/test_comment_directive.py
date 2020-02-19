import os

from mokuwiki import mokuwiki


def test_convert_comment(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

A line of text.

// A comment

Text ending in a // comment

''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert comments have been removed
    expect = f'''---
title: Page One
author: Phil
tags: [abc]
...

A line of text.



Text ending in a 

'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
