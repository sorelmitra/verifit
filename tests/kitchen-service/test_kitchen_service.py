import re
import subprocess


def test_ui():
    child = subprocess.run(
        ['yarn', 'cypress', 'run'],
        cwd='tests/kitchen-service/ui_test')
    assert child.returncode == 0
