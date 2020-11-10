import os

from page import Page

from utils import create_markdown_file, create_markdown_string, compare_markdown_content


def test_process_custom_style(tmpdir):
    source_dir = tmpdir.mkdir('source')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         'A ^^custom^^ style')

    page = Page(source_dir.join('file1.md'), None)
    page.process_directives()
    page.save(target_dir.join('file1.md'))

    expect = create_markdown_string({'title': 'Page One',
                                     'tags': '[abc]'},
                                    'A [custom]{.smallcaps} style')

    assert os.path.exists(target_dir.join('file1.md'))

    with open(target_dir.join('file1.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert compare_markdown_content(expect, actual)

# TODO test a link that has custom styling, but will need two pages in a namespace
