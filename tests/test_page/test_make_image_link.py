from mokuwiki.page import Page


def test_make_image_link():
    image_name = 'Image One'

    actual = Page.make_image_link(image_name)

    expect = '![Image One](image_one.jpg)'

    assert actual == expect


def test_make_image_link_ext():
    image_name = 'Image One'

    actual = Page.make_image_link(image_name, 'png')

    expect = '![Image One](image_one.png)'

    assert actual == expect


def test_make_image_link_media_dir():
    image_name = 'Image One'

    actual = Page.make_image_link(image_name, media_dir='test')

    expect = '![Image One](test/image_one.jpg)'

    assert actual == expect
