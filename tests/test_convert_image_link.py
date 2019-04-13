import os

from mokuwiki import mokuwiki


def test_convert_image_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

An image link: !!An Image!!
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

An image link: ![An Image](images/an_image.jpg)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_image_link_format(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

An image link: !!An Image|png!!
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

An image link: ![An Image](images/an_image.png)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_image_link_folder(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

An image link: !!An Image|png!!
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, media='media')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

An image link: ![An Image](media/an_image.png)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
