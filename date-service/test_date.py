import re
import subprocess


def test_date():
    child = subprocess.run(['date', '+DATE: %Y-%m-%d%nTIME: %H:%M:%S'], capture_output=True)
    output = child.stdout.decode('utf-8')
    print(output)
    lines = output.split('\n')
    assert lines is not None
    assert len(lines) >= 2
    assert re.match(r'DATE: \d{4}-\d{2}-\d{2}', lines[0])
    assert re.match(r'TIME: \d{2}:\d{2}:\d{2}', lines[1])
