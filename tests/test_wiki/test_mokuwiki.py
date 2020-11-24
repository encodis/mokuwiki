# TODO should test config and namespace overrides etc
# NOTE that most tests have set the default section of test.cfg to default in create_wiki_config()

import os

from mokuwiki.wiki import Wiki

from utils import create_wiki_config, create_markdown_file, create_markdown_string, compare_markdown_content


def test_multiple_namespaces(tmpdir):
    # two pages in same namespace, still need a wiki

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    source_dir.mkdir('ns2')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         'A link to [[ns2:Page Two]]')

    create_markdown_file(source_dir.join('ns2', 'file2.md'),
                         {'title': 'Page Two'},
                         'A link to [[ns1:Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)},
                       {'name': 'ns2',
                        'path': f'{source_dir.join("ns2")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert len(wiki) == 2
    assert len(wiki.namespaces['ns1']) == 1
    assert len(wiki.namespaces['ns2']) == 1

    expect1 = create_markdown_string({'title': 'Page One'},
                                     'A link to [Page Two](../ns2/page_two.html)')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)

    expect2 = create_markdown_string({'title': 'Page Two'},
                                     'A link to [Page One](../ns1/page_one.html)')

    assert os.path.exists(target_dir.join('ns2', 'page_two.md'))

    with open(target_dir.join('ns2', 'page_two.md'), 'r', encoding='utf8') as fh:
        actual2 = fh.read()

    assert compare_markdown_content(expect2, actual2)


def test_multiple_namespaces_aliases(tmpdir):
    # two pages in same namespace, still need a wiki

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    source_dir.mkdir('ns2')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         'A link to [[2nd Page|Y:Page Two]]')

    create_markdown_file(source_dir.join('ns2', 'file2.md'),
                         {'title': 'Page Two'},
                         'A link to [[X:Page One]]')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'alias': 'X',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)},
                       {'name': 'ns2',
                        'alias': 'Y',
                        'path': f'{source_dir.join("ns2")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    assert len(wiki) == 2
    assert len(wiki.namespaces['ns1']) == 1
    assert len(wiki.namespaces['ns2']) == 1

    expect1 = create_markdown_string({'title': 'Page One'},
                                     'A link to [2nd Page](../ns2/page_two.html)')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)

    expect2 = create_markdown_string({'title': 'Page Two'},
                                     'A link to [Page One](../ns1/page_one.html)')

    assert os.path.exists(target_dir.join('ns2', 'page_two.md'))

    with open(target_dir.join('ns2', 'page_two.md'), 'r', encoding='utf8') as fh:
        actual2 = fh.read()

    assert compare_markdown_content(expect2, actual2)
