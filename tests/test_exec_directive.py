import os

from mokuwiki import mokuwiki


def test_convert_exec_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
tags: [abc]
...

%% ls -1 -d "$PWD"/READ* %%

''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a listing of the README.md file
    expect = f'''---
title: Page One
tags: [abc]
...

{os.getcwd()}/README.md


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_exec_link_pipe(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
tags: [abc]
...

%% find "$PWD" -name READ*  | cat %%

''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a listing of the README.md file
    expect = f'''---
title: Page One
tags: [abc]
...

{os.getcwd()}/README.md


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
