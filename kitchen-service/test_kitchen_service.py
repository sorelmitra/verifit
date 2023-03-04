import re
import subprocess


def test_date():
    child = subprocess.run(
        ['yarn', 'cypress', 'run'],
        cwd='kitchen-service/ui_test')
    assert child.returncode == 0
