import os

from mokuwiki import mokuwiki


def test_report_broken(tmpdir, capsys):

    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
tags: [abc]
...

A link to [[Page Two]]
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, report=True)

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

    captured = capsys.readouterr()

    assert expect == actual
    assert captured.out == 'Page Two\n'
