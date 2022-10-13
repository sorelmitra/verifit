import os

import pytest

from config_tool import Config
from graphql_tool import GraphQLTool
from runner import runner


def test_hello():
    expected, actual = runner.cli(
        ["cp", "-v", runner.get_input_filename(), runner.get_output_filename()],
        check_token=['data.login.accessToken']) # demo of using check_token
    assert actual == expected


# The test doesn't check the results
# Instead, the 'checks' test does it below
def test_hello_delayed_1():
    _, filename = os.path.split(runner.get_input_filename())
    name, _ = os.path.splitext(filename)
    name = GraphQLTool.strip_input_suffix(name)
    Config.value[f'{name}_started'] = True
    Config.value[f'{name}_expected'] = name
    Config.value[f'{name}_actual'] = name


# The test doesn't check the results
#
# This test intentionally has a different `expected` and `actual`,
# to see how it behaves when using manual asserts when checking
# these values in the 'checks' test below
def test_hello_delayed_2():
    _, filename = os.path.split(runner.get_input_filename())
    name, _ = os.path.splitext(filename)
    name = GraphQLTool.strip_input_suffix(name)
    Config.value[f'{name}_started'] = True
    Config.value[f'{name}_expected'] = 'one two three'
    Config.value[f'{name}_actual'] = 'one three four'


# A second test that doesn't check the results
#
# This test intentionally has a different `expected` and `actual`,
# to see how it behaves when using manual asserts when checking
# these values in the 'checks' test below
@pytest.mark.order(after="test_hello_delayed_2")
def test_hello_delayed_3():
    _, filename = os.path.split(runner.get_input_filename())
    name, _ = os.path.splitext(filename)
    name = GraphQLTool.strip_input_suffix(name)
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


# Performs delayed checks on the previous two tests
# If any of them failed, it will fail
#
# Demonstrates tests order, as well
@pytest.mark.order(after="test_hello_delayed_3")
def test_hello_delayed_checks_first_fails():
    runner.assert_one_passed(['test_hello_delayed_3', 'test_hello_delayed_1'])


@pytest.mark.order(after="test_hello_delayed_3")
def test_hello_delayed_checks_second_fails():
    runner.assert_one_passed(['test_hello_delayed_1', 'test_hello_delayed_3'])


@pytest.mark.order(after="test_hello_delayed_3")
def test_hello_delayed_checks_misspelled_name_fails():
    runner.assert_one_passed(['test_hello_delayed_4', 'test_hello_delayed_1'])


@pytest.mark.order(after="test_hello_delayed_3")
def test_hello_delayed_checks_both_fail():
    runner.assert_one_passed(['test_hello_delayed_2', 'test_hello_delayed_3'])
