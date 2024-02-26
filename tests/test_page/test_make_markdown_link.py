from mokuwiki.utils import make_markdown_link


def test_make_markdown_link():
    show_name = 'Page One'
    page_name = 'page_one'

    actual = make_markdown_link(show_name, page_name)

    expect = '[Page One](page_one.html)'

    assert actual == expect


def test_make_markdown_link_namespace():
    show_name = 'Page One'
    namespace = 'test'
    page_name = 'page_one'

    actual = make_markdown_link(show_name, page_name, ns_path=namespace)

    expect = '[Page One](../test/page_one.html)'

    assert actual == expect
