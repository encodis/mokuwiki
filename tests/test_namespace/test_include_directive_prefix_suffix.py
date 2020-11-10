import os

from mokuwiki import mokuwiki


# helper function to create pages
def make_test_page(title, tags, content=''):
    return f'''---
title: {title}
tags: [{tags}]
prefix: "This is a prefix\n\n"
suffix: "\n\nThis is a suffix"
...

{content}
'''


def test_replace_included_prefix_suffix(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', f'<<{tmpdir}/source/file2.md>>'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'xyz', 'The title is Page Two'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has contents of page_two
    expect = '''---
title: Page One
tags: [abc]
prefix: "This is a prefix\n\n"
suffix: "\n\nThis is a suffix"
...

This is a prefix


The title is Page Two

This is a suffix


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
