import os

from mokuwiki import mokuwiki


# helper function to create pages
def make_test_page(title, tags, content=''):
    return f'''---
title: {title}
tags: [{tags}]
...

{content}
'''


def test_convert_tags_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{abc}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has links to pages with tag 'abc'
    expect = '''---
title: Page One
tags: [abc]
...

[Page One](page_one.html)

[Page Two](page_two.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_no_tag(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', '', '{{abc}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has links to pages with tag 'abc' (which does not include page_one.md)
    expect = '''---
title: Page One
tags: []
...

[Page Two](page_two.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_or(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{abc def}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'def'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has links to pages with tags 'abc' OR 'def'
    expect = '''---
title: Page One
tags: [abc]
...

[Page One](page_one.html)

[Page Two](page_two.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_and(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{abc +def}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc, def'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has links to pages with both tags 'abc' AND 'def'
    expect = '''---
title: Page One
tags: [abc]
...

[Page Two](page_two.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_not(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{abc -def}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc, def'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a link to pages with tags 'abc' but NOT if they also have 'def'
    expect = '''---
title: Page One
tags: [abc]
...

[Page One](page_one.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_all(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{*}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a link to all pages
    expect = '''---
title: Page One
tags: [abc]
...

[Page One](page_one.html)

[Page Three](page_three.html)

[Page Two](page_two.html)
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_number_all(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{#}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has the number of pages with a tag
    expect = '''---
title: Page One
tags: [abc]
...

3
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_number_tag(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{#abc}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc, def'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has the number of pages with tag 'abc
    expect = '''---
title: Page One
tags: [abc]
...

2
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_list(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{@}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc, def'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a list of all tags
    expect = '''---
title: Page One
tags: [abc]
...

[abc]{.tag}

[def]{.tag}

[xyz]{.tag}
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_list_alt(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write(make_test_page('Page One', 'abc', '{{@}}'))

    file2 = source_dir.join('file2.md')
    file2.write(make_test_page('Page Two', 'abc, def'))

    file3 = source_dir.join('file3.md')
    file3.write(make_test_page('Page Three', 'xyz'))

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, tag='alt_tag')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md has a list of all tags, alternate class
    expect = '''---
title: Page One
tags: [abc]
...

[abc]{.alt_tag}

[def]{.alt_tag}

[xyz]{.alt_tag}
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
