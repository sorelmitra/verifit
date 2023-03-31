import subprocess


def test_ui():
    child = subprocess.run(
        ['yarn', 'cypress', 'run'],
        cwd='kitchen_service/ui_test')
    assert child.returncode == 0
