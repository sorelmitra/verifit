import json

from runner import runner


# The expected output of this test is slightly modified,
# so you can see a test failure in action
def test_rest_api_post_1():
    expected, actual = runner.rest(path='/posts', method='POST')
    assert actual == expected


def test_rest_api_get_sorted():
    expected, actual = runner.rest(path='/todos', method='GET', use_input_file=False,
                                   sort=[{'list': '', 'field': 'title'}])  # sort top list by title
    assert actual == expected


def test_rest_api_get_strip_regex():
    expected, actual = runner.rest(path='/todos/1', method='GET', use_input_file=False,
                                   strip_regex=[r'"id": (\d+),.*\n'])  # strip id from response with regex
    assert actual == expected
    assert ['"id": 1,\n'] == runner.get_stripped_values()


def test_rest_api_get_strip_keys():
    expected, actual = runner.rest(path='/todos/1', method='GET', use_input_file=False,
                                   strip_keys=['id'])  # strip id from response with keys
    assert actual == expected
    assert 1 == runner.get_stripped_values()[0]


def test_rest_api_get_strip_key_values_regex():
    expected, actual = runner.rest(path='/todos', method='GET', use_input_file=False,
                                   strip_key_values_regex=[{
                                       'key': '',
                                       'type': 'list',
                                       'sub_key': 'title',
                                       'value_regex': r'.*qui.*'
                                   }])  # strip objects whose 'title' contains 'qui'
    assert actual == expected
    with open(f"{runner.get_filename_with_suffix('-stripped')}") as f:
        stripped_values = json.load(f)
        assert stripped_values == runner.get_stripped_values()


def test_rest_api_filetype():
    expected, actual = runner.rest(path='/posts', method='POST', filetype='txt') # use txt filetype
    assert actual == expected
