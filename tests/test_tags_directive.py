import os

from mokuwiki import mokuwiki


def test_convert_tags_link(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing tag 'abc':

{{abc}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing tag 'abc':

[Page One](page_one.html)

[Page Two](page_two.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_no_tag(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
...

Pages containing tag 'abc':

{{abc}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
...

Pages containing tag 'abc':

[Page Two](page_two.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_or(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing tags 'abc' or 'def':

{{abc def}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [def]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing tags 'abc' or 'def':

[Page One](page_one.html)

[Page Two](page_two.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_and(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing tags 'abc' and 'def':

{{abc +def}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc, def]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing tags 'abc' and 'def':

[Page Two](page_two.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_not(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing tags 'abc' and not 'def':

{{abc -def}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc, def]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing tags 'abc' and not 'def':

[Page One](page_one.html)


'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_all(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing all tags:

{{*}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing all tags:

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
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing all tags:

{{#}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing all tags:

3
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_number_tag(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing all tags:

{{#abc}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc, def]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

Pages containing all tags:

2
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual


def test_convert_tags_link_list(tmpdir):
    source_dir = tmpdir.mkdir('source')

    file1 = source_dir.join('file1.md')
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

List of tags:

{{@}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc, def]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir)

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

List of tags:

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
    file1.write('''---
title: Page One
author: Phil
tags: [abc]
...

List of tags:

{{@}}
''')

    file2 = source_dir.join('file2.md')
    file2.write('''---
title: Page Two
author: Phil
tags: [abc, def]
...

This is Page Two
''')

    file3 = source_dir.join('file3.md')
    file3.write('''---
title: Page Three
author: Phil
tags: [xyz]
...

This is Page Three
''')

    target_dir = tmpdir.mkdir('target')

    mokuwiki(source_dir, target_dir, tag='alt_tag')

    # assert correct output files exist
    assert os.path.exists(os.path.join(target_dir, 'page_one.md'))

    # assert contents of page_one.md have a link to page_two.md
    expect = '''---
title: Page One
author: Phil
tags: [abc]
...

List of tags:

[abc]{.alt_tag}

[def]{.alt_tag}

[xyz]{.alt_tag}
'''

    with open(os.path.join(target_dir, 'page_one.md'), 'r', encoding='utf8') as fh:
        actual = fh.read()

    assert expect == actual
