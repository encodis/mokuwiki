import os

from page import Page

from utils import create_markdown_file, create_markdown_string, compare_markdown_content


def test_process_exec_command(tmpdir):
    source_dir = tmpdir.mkdir('source')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '%% ls -1 -d "$PWD"/READ* %%')

    page = Page(source_dir.join('file1.md'), None)
    page.process_directives()
    page.save(target_dir.join('file1.md'))

    expect = create_markdown_string({'title': 'Page One',
                                     'tags': '[abc]'},
                                    f'{os.getcwd()}/README.md\n')

    assert os.path.exists(target_dir.join('file1.md'))

    with open(os.path.join(target_dir, 'file1.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert compare_markdown_content(expect, actual)


def test_process_exec_command_pipe(tmpdir):
    source_dir = tmpdir.mkdir('source')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '%% find "$PWD" -name READ*  | cat %%')

    page = Page(source_dir.join('file1.md'), None)
    page.process_directives()
    page.save(target_dir.join('file1.md'))

    expect = create_markdown_string({'title': 'Page One',
                                     'tags': '[abc]'},
                                    f'{os.getcwd()}/README.md\n')

    assert os.path.exists(target_dir.join('file1.md'))

    with open(os.path.join(target_dir, 'file1.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert compare_markdown_content(expect, actual)
