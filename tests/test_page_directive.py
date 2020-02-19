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


def test_convert_page_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two]] and another link to [[Page Two]]'))

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

A link to [Page Two](page_two.html) and another link to [Page Two](page_two.html)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_page_link_alias(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two]] and a link to its alias [[2nd Page]]'))

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
alias: 2nd Page
tags: [abc]
...

This is Page Two
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a link to page_two.html and another via its alias
    expect = '''---
title: Page One
tags: [abc]
...

A link to [Page Two](page_two.html) and a link to its alias [2nd Page](page_two.html)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_page_link_display(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[P2|Page Two]]'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a link to page_two.md via its display name
    expect = '''---
title: Page One
tags: [abc]
...

A link to [P2](page_two.html)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_page_link_broken(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two]]'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a link to page_two tagged as broken
    expect = '''---
title: Page One
tags: [abc]
...

A link to [Page Two]{.broken}
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_page_link_alt_broken(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[Page Two]]'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, broken='not_found')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a link to page_two tagged as not_found
    expect = '''---
title: Page One
tags: [abc]
...

A link to [Page Two]{.not_found}
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_page_link_namespace(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[ns:Page Two]]'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a link to page_two.html in a different namespace
    expect = '''---
title: Page One
tags: [abc]
...

A link to [Page Two](../ns/page_two.html)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_page_link_namespace_full(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', 'A link to [[..ns:Page Two]]'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, fullns=True)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.html using full namespace
    expect = '''---
title: Page One
tags: [abc]
...

A link to [Page Two](..ns/page_two.html)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual

# TODO test_convert_page_link_dot_file - these are not included by default?
