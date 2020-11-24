import os

from wiki import Wiki

from utils import create_wiki_config, create_markdown_file, create_markdown_string, compare_markdown_content


def test_process_page_links(tmpdir):
    # two pages in same namespace, still need a wiki

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         'A link to [[Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert len(wiki) == 1
    assert len(wiki.namespaces['ns1']) == 2

    expect1 = create_markdown_string({'title': 'Page One'},
                                     'A link to [Page Two](page_two.html)')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)

    expect2 = create_markdown_string({'title': 'Page Two'},
                                     'A link to [Page One](page_one.html)')

    assert os.path.exists(target_dir.join('ns1', 'page_two.md'))

    with open(target_dir.join('ns1', 'page_two.md'), 'r', encoding='utf8') as fh:
        actual2 = fh.read()

    assert compare_markdown_content(expect2, actual2)


def test_process_page_links_alias(tmpdir):

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         'A link to [[2nd Page]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'alias': '2nd Page'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert len(wiki) == 1
    assert len(wiki.namespaces['ns1']) == 2

    expect1 = create_markdown_string({'title': 'Page One'},
                                     'A link to [2nd Page](page_two.html)')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)

    expect2 = create_markdown_string({'title': 'Page Two',
                                      'alias': '2nd Page'},
                                     'A link to [Page One](page_one.html)')

    assert os.path.exists(target_dir.join('ns1', 'page_two.md'))

    with open(target_dir.join('ns1', 'page_two.md'), 'r', encoding='utf8') as fh:
        actual2 = fh.read()

    assert compare_markdown_content(expect2, actual2)


def test_process_page_links_display(tmpdir):
    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         'A link to [[P2|Page Two]]')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two'},
                         'A link to [[Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert len(wiki) == 1
    assert len(wiki.namespaces['ns1']) == 2

    expect1 = create_markdown_string({'title': 'Page One'},
                                     'A link to [P2](page_two.html)')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)

    expect2 = create_markdown_string({'title': 'Page Two'},
                                     'A link to [Page One](page_one.html)')

    assert os.path.exists(target_dir.join('ns1', 'page_two.md'))

    with open(target_dir.join('ns1', 'page_two.md'), 'r', encoding='utf8') as fh:
        actual2 = fh.read()

    assert compare_markdown_content(expect2, actual2)


def test_process_page_links_broken(tmpdir):
    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         'A link to [[Page Two]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert len(wiki) == 1
    assert len(wiki.namespaces['ns1']) == 1

    expect1 = create_markdown_string({'title': 'Page One'},
                                     'A link to [Page Two]{.broken}')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)

# TODO alternate CSS for broken link ?


def test_process_page_links_metadata_string(tmpdir):
    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'subtitle': 'Page Two'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two'},
                         'Text')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'meta_fields': 'subtitle'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert len(wiki) == 1
    assert len(wiki.namespaces['ns1']) == 2

    expect1 = create_markdown_string({'title': 'Page One',
                                      'subtitle': "'[Page Two](page_two.html)'"},
                                     'Text')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_page_links_metadata_list(tmpdir):
    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[Page Two, Page Three]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three'},
                         'Text')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'meta_fields': 'tags'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert len(wiki) == 1
    assert len(wiki.namespaces['ns1']) == 3

    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': ['[Page Two](page_two.html)', '[Page Three](page_three.html)']},
                                     'Text')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)
