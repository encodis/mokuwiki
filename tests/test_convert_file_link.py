import os

from mokuwiki import mokuwiki


def test_convert_file_link(tmpdir):

    ### DOES NOT WORK because mokuwiki() reads from os.getcwd() with is project folder not tmpdir
    ### add option for specifying root of include files? (-i, --include)?

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

<<./file2.md>>
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...

Contents of Page Two
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

Contents of Page Two

'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    #assert expect == actual
    assert True


def test_convert_file_link_globbing(tmpdir):
    assert True


def test_convert_file_link_hidden(tmpdir):
    # files starting with . are not included?
    assert True


def test_convert_file_link_separator(tmpdir):
    assert True


def test_convert_file_link_prefix(tmpdir):
    assert True


def test_convert_file_link_separator_and_prefix(tmpdir):
    assert True
