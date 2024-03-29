from mokuwiki.utils import make_markdown_span


def test_make_markdown_span():
    page_name = 'Page One'

    actual = make_markdown_span(page_name)

    expect = '[Page One]'

    assert actual == expect


def test_make_markdown_link_namespace():
    page_name = 'Page One'
    css_class = '.test'

    actual = make_markdown_span(page_name, css_class=css_class)

    expect = '[Page One]{.test}'

    assert actual == expect
