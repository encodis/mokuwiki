from mokuwiki.utils import make_file_name


def test_make_file_name():
    source = 'Page One'
    actual = make_file_name(source)
    expect = 'page_one'

    assert actual == expect


def test_make_file_name_with_ext():
    source = 'Page One'
    actual = make_file_name(source, 'md')
    expect = 'page_one.md'

    assert actual == expect
