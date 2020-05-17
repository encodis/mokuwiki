import os

from mokuwiki import mokuwiki


# helper function to create pages
def make_test_page(title, tags, content=''):
    return f'''---
title: {title}
tags: {tags}
...

{content}
'''


def test_replace_included_metadata(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md>>'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'xyz', 'The title is ?{title}'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of page_two
    expect = '''---
title: Page One
tags: abc
...



The title is Page Two



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_replace_included_metadata_off(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md>>'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'xyz', 'The title is ?{title}'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, replace=False)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of page_two
    expect = '''---
title: Page One
tags: abc
...



The title is ?{title}



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_replace_included_metadata_multiple(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md>>'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'xyz', 'The title is ?{title} with tags ?tags'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of page_two
    expect = '''---
title: Page One
tags: abc
...



The title is Page Two with tags xyz



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_replace_included_metadata_multiline(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md>>'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'xyz', '''The title is ?{title}
with tags ?{tags}'''))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of page_two
    expect = '''---
title: Page One
tags: abc
...



The title is Page Two
with tags xyz



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_replace_included_math(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md>>'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'xyz', 'Here is some $$math$$'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of page_two
    expect = '''---
title: Page One
tags: abc
...



Here is some $$math$$



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual

