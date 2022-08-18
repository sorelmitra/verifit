import os
import subprocess

from exceptions import RunException
from relative_path import RelativePath
from results import Results


class BasicRunner(RelativePath):
    def __init__(self):
        super().__init__()

    def get_input_filename(self, offset=0):
        return self._get_filename(offset=offset)

    def get_output_filename(self, offset=0):
        return self._get_filename(suffix='-answer', offset=offset)

    def get_expected_output_filename(self, offset=0):
        return self._get_filename(suffix='-expected', offset=offset)

    def run(self, command=None, func=None,
            update_snapshot=False,
            strip_regex=None, strip_keys=None, strip_key_values_regex=None,
            sort=None, use_expected_output=True):
        if command is None and func is None:
            raise RunException("Either command or func must be specified")
        elif command is not None and func is not None:
            raise RunException("Only one of command or func must be specified")

        try:
            os.unlink(self.get_output_filename(offset=1))
        except FileNotFoundError:
            pass

        if command is None:
            func()
        else:
            subprocess.run(command)

        # print('XXXXXXXX', 'getting results')
        results = Results(use_expected_output=use_expected_output,
                          expected_output_filename=self.get_expected_output_filename(offset=1),
                          output_filename=self.get_output_filename(offset=1),
                          update_snapshot=update_snapshot,
                          strip_regex=strip_regex,
                          strip_keys=strip_keys,
                          strip_key_values_regex=strip_key_values_regex,
                          sort=sort)
        return results.get_and_update()

