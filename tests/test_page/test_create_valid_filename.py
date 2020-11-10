from page import create_valid_filename


def test_create_valid_filename():
    source = 'Page One'
    actual = create_valid_filename(source)
    expect = 'page_one'

    assert actual == expect


def test_create_valid_filename_with_ext():
    source = 'Page One'
    actual = create_valid_filename(source, 'md')
    expect = 'page_one.md'

    assert actual == expect
