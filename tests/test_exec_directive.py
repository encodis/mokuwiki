import os

from mokuwiki import mokuwiki


def test_convert_exec_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

A file listing:

%% ls READ* %%

''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    cwd = os.getcwd()

    # update expected text with CWD
    expect = f'''---
title: Page One
author: Phil
tags: [abc]
...

A file listing:

{cwd}/README.md


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
