import os

from mokuwiki import mokuwiki


def test_mokuwiki(tmpdir):
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

A link to [[Page One]]
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, 'page_two.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect_one = '''---
title: Page One
author: Phil
tags: [abc]
...

A link to [Page Two](page_two.html)
'''

    expect_two = '''---
title: Page Two
author: Phil
tags: [abc]
...

A link to [Page One](page_one.html)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as f1:
        actual_one = f1.read()

    with open(os.path.join(target_dir, 'page_two.md'), 'r', encoding='utf8') as f2:
        actual_two = f2.read()

    assert expect_one == actual_one
    assert expect_two == actual_two


def test_mokuwiki_ellipses(tmpdir):
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

Some text... or is it?

A link to [[Page One]]
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))
    assert os.path.exists(os.path.join(target_dir, 'page_two.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect_one = '''---
title: Page One
author: Phil
tags: [abc]
...

A link to [Page Two](page_two.html)
'''

    expect_two = '''---
title: Page Two
author: Phil
tags: [abc]
...

Some text... or is it?

A link to [Page One](page_one.html)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as f1:
        actual_one = f1.read()

    with open(os.path.join(target_dir, 'page_two.md'), 'r', encoding='utf8') as f2:
        actual_two = f2.read()

    assert expect_one == actual_one
    assert expect_two == actual_two
