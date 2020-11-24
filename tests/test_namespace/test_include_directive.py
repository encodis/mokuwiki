import os

from mokuwiki.wiki import Wiki

from utils import create_wiki_config, create_markdown_file, create_markdown_string, compare_markdown_content


def test_process_file_includes(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         f'<<{source_dir.join("ns1", "file2.md")}>>')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two'},
                         'Included Text')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    expect1 = create_markdown_string({'title': 'Page One'},
                                     '''Included Text''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_file_includes_globbing(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         f'<<{source_dir.join("ns1", "fileX*.md")}>>')

    create_markdown_file(source_dir.join('ns1', 'fileX2.md'),
                         {'title': 'Page Two'},
                         'Included Text 2')

    create_markdown_file(source_dir.join('ns1', 'fileX3.md'),
                         {'title': 'Page Three'},
                         'Included Text 3')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    expect1 = create_markdown_string({'title': 'Page One'},
                                     '''Included Text 2

Included Text 3''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_file_includes_separator(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         f'<<{source_dir.join("ns1", "fileX*.md|* * *")}>>')

    create_markdown_file(source_dir.join('ns1', 'fileX2.md'),
                         {'title': 'Page Two'},
                         'Included Text 2')

    create_markdown_file(source_dir.join('ns1', 'fileX3.md'),
                         {'title': 'Page Three'},
                         'Included Text 3')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    expect1 = create_markdown_string({'title': 'Page One'},
                                     '''Included Text 2

* * *

Included Text 3''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_file_includes_line_prefix(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         f'<<{source_dir.join("ns1", "file2.md")}||> >>')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two'},
                         '''Included Text''')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    expect1 = create_markdown_string({'title': 'Page One'},
                                     '''> Included Text''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_file_includes_separator_and_line_prefix(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         f'<<{source_dir.join("ns1", "fileX*.md")}|* * *|> >>')

    create_markdown_file(source_dir.join('ns1', 'fileX2.md'),
                         {'title': 'Page Two'},
                         'Included Text 2')

    create_markdown_file(source_dir.join('ns1', 'fileX3.md'),
                         {'title': 'Page Three'},
                         'Included Text 3')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    expect1 = create_markdown_string({'title': 'Page One'},
                                     '''> Included Text 2

* * *

> Included Text 3''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_file_includes_prefix_and_suffix(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         f'<<{source_dir.join("ns1", "file2.md")}>>')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'prefix': '"The prefix line\n\n"',
                          'suffix': '"\n\nThe suffix line"'},
                         'Included Text')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    expect1 = create_markdown_string({'title': 'Page One'},
                                     '''The prefix line
Included Text
The suffix line''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_file_includes_metadata_replace(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         f'<<{source_dir.join("ns1", "file2.md")}>>')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two'},
                         'Included page is ?{title}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    expect1 = create_markdown_string({'title': 'Page One'},
                                     '''Included page is Page Two''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_file_includes_metadata_replace_multi(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         f'<<{source_dir.join("ns1", "file2.md")}>>')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'subtitle': 'Second Page'},
                         'Included page is ?{title} with subtitle ?{subtitle}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    expect1 = create_markdown_string({'title': 'Page One'},
                                     '''Included page is Page Two with subtitle Second Page''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)
