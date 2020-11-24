from page import Page


def test_slugify():
    source = 'Page One'
    actual = Page.slugify(source)
    expect = 'page_one'

    assert actual == expect


def test_slugify_with_ext():
    source = 'Page One'
    actual = Page.slugify(source, 'md')
    expect = 'page_one.md'

    assert actual == expect
