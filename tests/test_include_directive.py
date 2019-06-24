import os

from mokuwiki import mokuwiki


def test_convert_file_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(f'''---
title: Page One
author: Phil
tags: [abc]
...

<<{tmpdir}/source/file2.md>>
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

    assert expect == actual


def test_convert_file_link_globbing(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(f'''---
title: Page One
author: Phil
tags: [abc]
...

<<{tmpdir}/source/fileX*.md>>
''')

    file2 = source_dir.join('fileX2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...

Contents of Page Two

''')

    file3 = source_dir.join('fileX3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [abc]
...

Contents of Page Three

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







Contents of Page Three




'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_file_link_separator(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(f'''---
title: Page One
author: Phil
tags: [abc]
...

<<{tmpdir}/source/fileX*.md|* * *>>
''')

    file2 = source_dir.join('fileX2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...
Contents of Page Two
''')

    file3 = source_dir.join('fileX3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [abc]
...
Contents of Page Three
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


* * *


Contents of Page Three



'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_file_link_prefix(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(f'''---
title: Page One
author: Phil
tags: [abc]
...

<<{tmpdir}/source/file2.md||> >>
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

    # assert contents of page_one.md has contents of file2.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

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
    file1.write(f'''---
title: Page One
author: Phil
tags: [abc]
...

<<{tmpdir}/source/fileX*.md|* * *|> >>
''')

    file2 = source_dir.join('fileX2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...
Contents of Page Two
''')

    file3 = source_dir.join('fileX3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [abc]
...
Contents of Page Three
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

> 
> Contents of Page Two
> 

* * *

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
    file1.write(f'''---
title: Page One
author: Phil
tags: [abc]
...

<<{tmpdir}/source/file2.md>>
''')

    file2 = source_dir.join('file2.md')
    file2.write('''
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

    assert expect == actual
