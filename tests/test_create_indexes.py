import os

from mokuwiki import mokuwiki


def test_create_indexes(tmpdir):
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
title: Page One
author: Phil
tags: [xyz]
...

A link to [[Page One]]
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, verbose=True)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert not os.path.exists(os.path.join(target_dir, 'page_two.md'))

    # assert contents of page_one.md has a broken link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

A link to [Page Two]{.broken}
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as f1:
        actual = f1.read()

    assert expect == actual
