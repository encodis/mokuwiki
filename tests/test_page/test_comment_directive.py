import os

from page import Page

from utils import create_markdown_file, create_markdown_string, compare_markdown_content

# these tests can be done in single file mode, as we're just testing page functionality


def test_convert_comment(tmpdir):
    source_dir = tmpdir.mkdir('source')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '''A line of text.

// A comment

Text ending in a // comment
''')

    page = Page(source_dir.join('file1.md'), None)
    page.process_directives()
    page.save(target_dir.join('file1.md'))

    expect = create_markdown_string({'title': 'Page One',
                                     'tags': '[abc]'},
                                    '''A line of text.



Text ending in a 
''')

    assert os.path.exists(target_dir.join('file1.md'))

    with open(target_dir.join('file1.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert compare_markdown_content(expect, actual)
