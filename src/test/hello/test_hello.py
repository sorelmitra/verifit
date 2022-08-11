from runner import *


def test_hello():
    expected, actual = runner.cli(["cp", "-v", runner.get_input_filename(), runner.get_output_filename()])
    assert actual == expected
