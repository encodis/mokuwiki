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


def test_convert_file_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md>>'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc', 'Contents of Page Two'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of page_two
    expect = '''---
title: Page One
tags: [abc]
...



Contents of Page Two



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_file_link_globbing(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/fileX*.md>>'))

    file2 = source_dir.join('fileX2.md')
    file2.write(make_test_page('Page Two', 'abc', 'Contents of Page Two'))

    file3 = source_dir.join('fileX3.md')
    file3.write(make_test_page('Page Three', 'abc', 'Contents of Page Three'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of pages 2 and 3
    expect = '''---
title: Page One
tags: [abc]
...



Contents of Page Two






Contents of Page Three



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_file_link_separator(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/fileX*.md|* * *>>'))

    file2 = source_dir.join('fileX2.md')
    file2.write(make_test_page('Page Two', 'abc', 'Contents of Page Two'))

    file3 = source_dir.join('fileX3.md')
    file3.write(make_test_page('Page Three', 'abc', 'Contents of Page Three'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of pages 2 and 3 with separator
    expect = '''---
title: Page One
tags: [abc]
...



Contents of Page Two


* * *



Contents of Page Three



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_file_link_prefix(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md||> >>'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc', 'Contents of Page Two'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of file2.md with prefix
    expect = '''---
title: Page One
tags: [abc]
...

> 
> 
> Contents of Page Two
> 


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_file_link_separator_and_prefix(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/fileX*.md|* * *|> >>'))

    file2 = source_dir.join('fileX2.md')
    file2.write(make_test_page('Page Two', 'abc', 'Contents of Page Two'))

    file3 = source_dir.join('fileX3.md')
    file3.write(make_test_page('Page Three', 'abc', 'Contents of Page Three'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of pages 2 and 3 with prefix and separator
    expect = '''---
title: Page One
tags: [abc]
...

> 
> 
> Contents of Page Two
> 

* * *

> 
> 
> Contents of Page Three
> 


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_file_plain(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md>>'))

    file2 = source_dir.join('file2.md')
    file2.write('''
Contents of Page Two

''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of page 2
    expect = '''---
title: Page One
tags: [abc]
...


Contents of Page Two




'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
