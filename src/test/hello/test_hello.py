from runner import runner


def test_hello():
    expected, actual = runner.cli(
        ["cp", "-v", runner.get_input_filename(), runner.get_output_filename()],
        check_token=['data.login.accessToken']) # demo of using check_token
    assert actual == expected
