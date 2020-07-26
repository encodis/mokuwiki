import os

from mokuwiki import mokuwiki


# helper function to create pages
def make_test_page(title, tags, content=''):
    return f'''---
title: {title}
tags: [{tags}]
...

{content}
'''


def test_convert_custom_style(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'This is ^^a custom^^ style'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has two links to page_two.html
    expect = '''---
title: Page One
tags: [abc]
...

This is [a custom]{.smallcaps} style
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_custom_style_custom(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'This is ^^a custom^^ style'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, custom='.foo')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has two links to page_two.html
    expect = '''---
title: Page One
tags: [abc]
...

This is [a custom]{.foo} style
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_custom_style_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'This is a styled ^^[[Page Two]]^^ link'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has two links to page_two.html
    expect = '''---
title: Page One
tags: [abc]
...

This is a styled [[Page Two](page_two.html)]{.smallcaps} link
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
