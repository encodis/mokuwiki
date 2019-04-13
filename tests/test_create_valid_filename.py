from mokuwiki import create_valid_filename


def test_create_valid_filename():
    source = 'Page One'
    actual = create_valid_filename(source)
    expect = 'page_one'

    assert actual == expect
