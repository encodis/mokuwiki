import os

from mokuwiki.wiki import Wiki

from utils import create_wiki_config, create_markdown_file, create_markdown_string, compare_markdown_content


def test_process_tags_directive(tmpdir):
    """Test that the directive '{{tag}}' produces a list of pages with that tag,
    and that pages without those tags are not included in the list
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{abc}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert page 3 not in list as it is not tagged 'abc'
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[Page One](page_one.html)

[Page Two](page_two.html)

''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    # assert page 3 only contains itself, as only it is tagged 'xyz'
    assert compare_markdown_content(expect1, actual1)

    expect3 = create_markdown_string({'title': 'Page Three',
                                      'tags': '[xyz]'},
                                     '''[Page Three](page_three.html)

''')

    assert os.path.exists(target_dir.join('ns1', 'page_three.md'))

    with open(target_dir.join('ns1', 'page_three.md'), 'r', encoding='utf8') as fh:
        actual3 = fh.read()

    assert compare_markdown_content(expect3, actual3)


def test_process_tags_directive_or(tmpdir):
    """Test OR
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{abc def}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert page 3 not in list as it is not tagged 'abc'
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[Page One](page_one.html)

[Page Two](page_two.html)

''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_tags_directive_and(tmpdir):
    """Test AND
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{abc +def}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc, def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert page 3 not in list as it is not tagged 'abc'
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[Page Two](page_two.html)

''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_tags_directive_and_three(tmpdir):
    """Test AND
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{abc +def +ghi}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc, def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_markdown_file(source_dir.join('ns1', 'file4.md'),
                         {'title': 'Page Four',
                          'tags': '[abc, def, ghi]'},
                         'Text')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert page 4 only one with all three tags
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[Page Four](page_four.html)

''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_tags_directive_not(tmpdir):
    """Test NOT
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{abc -def}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc, def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert page 3 not in list as it is not tagged 'abc'
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[Page One](page_one.html)

''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_tags_directive_not_and(tmpdir):
    """Test NOT
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{abc +def -ghi}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc, def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[abc, def, ghi, jkl]'},
                         'Text')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert page 4 not in list, has def but also ghi
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[Page Two](page_two.html)

''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_tags_directive_list_all(tmpdir):
    """Test LIST ALL
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{*}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert all pages are listed. NOTE: list is alphabetical (Three before Two!)
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[Page One](page_one.html)

[Page Three](page_three.html)

[Page Two](page_two.html)''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_tags_directive_count_all(tmpdir):
    """Test COUNT ALL
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{#}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert all pages are counted
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''3''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_tags_directive_count_tag(tmpdir):
    """Test COUNT TAG
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{#abc}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc, def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert all pages are counted
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''2''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)


def test_process_tags_directive_list_tags(tmpdir):
    """Test LIST TAGS
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{@}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc, def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir)})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert all pages are counted
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[abc]{.tag}

[def]{.tag}

[xyz]{.tag}''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)

def test_process_tags_directive_noise(tmpdir):
    """Test LIST TAGS
    """

    source_dir = tmpdir.mkdir('source')
    source_dir.mkdir('ns1')
    target_dir = tmpdir.mkdir('target')

    create_markdown_file(source_dir.join('ns1', 'file1.md'),
                         {'title': 'Page One',
                          'tags': '[abc]'},
                         '{{@}}')

    create_markdown_file(source_dir.join('ns1', 'file2.md'),
                         {'title': 'Page Two',
                          'tags': '[abc, def]'},
                         'Text')

    create_markdown_file(source_dir.join('ns1', 'file3.md'),
                         {'title': 'Page Three',
                          'tags': '[xyz]'},
                         '{{xyz}}')

    create_wiki_config(str(source_dir.join('test.cfg')),
                       None,
                       {'name': 'ns1',
                        'path': f'{source_dir.join("ns1")}',
                        'target': str(target_dir),
                        'noise_tags': 'xyz'})

    wiki = Wiki(source_dir.join('test.cfg'))

    wiki.process_namespaces()

    # assert all pages are counted
    expect1 = create_markdown_string({'title': 'Page One',
                                      'tags': '[abc]'},
                                     '''[abc]{.tag}

[def]{.tag}''')

    assert os.path.exists(target_dir.join('ns1', 'page_one.md'))

    with open(target_dir.join('ns1', 'page_one.md'), 'r', encoding='utf8') as fh:
        actual1 = fh.read()

    assert compare_markdown_content(expect1, actual1)
