import pytest

from config_tool import Config
from runner import runner


def test_hello():
    expected, actual = runner.cli(
        ["cp", "-v", runner.get_input_filename(), runner.get_output_filename()],
        check_token=['data.login.accessToken']) # demo of using check_token
    assert actual == expected


def test_hello_collect_1():
    name = 'test_hello_collect_1'
    Config.value[f'{name}_started'] = True
    Config.value[f'{name}_expected'] = name
    Config.value[f'{name}_actual'] = name


# This test intentionally has a different `expected` and `actual`,
# to see how it behaves when using manual asserts when checking
# these values in the 'checks' test below
@pytest.mark.order(after="test_hello_collect_1")
def test_hello_collect_2():
    name = 'test_hello_collect_2'
    Config.value[f'{name}_started'] = True
    Config.value[f'{name}_expected'] = """
    abc
    def
    ghi
    """
    Config.value[f'{name}_actual'] = """
    abc
    defGGG
    ghi
    """


# Demonstrates tests order, as well
@pytest.mark.order(after="test_hello_collect_2")
def test_hello_collect_checks():
    passed = True
    if Config.value.get('test_hello_collect_1_started', False):
        expected = Config.value.get('test_hello_collect_1_expected', '')
        actual = Config.value.get('test_hello_collect_1_actual', '')
        passed = runner.did_it_pass('test_hello_collect_1', expected, actual) and passed
    if Config.value.get('test_hello_collect_2_started', False):
        expected = Config.value.get('test_hello_collect_2_expected', '')
        actual = Config.value.get('test_hello_collect_2_actual', '')
        passed = runner.did_it_pass('test_hello_collect_2', expected, actual) and passed
    assert passed
