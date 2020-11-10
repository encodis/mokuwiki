import os

from namespace import Namespace

from utils import create_markdown_file, create_markdown_string, compare_markdown_content


def test_process_page_links_namespace(tmpdir):
    source_dir = tmpdir.mkdir('source')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One'},
                         'A link to [[ns2:Page Two]]')

    create_markdown_file(source_dir.join('ns2', 'file2.md'),
                         {'title': 'Page Two'},
                         'A link to [[ns1:Page One]]')

    ns1 = Namespace({'name': 'ns1',
                     'path': source_dir.join('ns1')},
                    None)

    ns2 = Namespace({'name': 'ns2',
                     'path': source_dir.join('ns2')},
                    None)

    # TODO create wiki 

    ns1.update_index()
    ns1.process_pages()

    ns2.update_index()
    ns2.process_pages()

    assert len(ns1) == 2

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
