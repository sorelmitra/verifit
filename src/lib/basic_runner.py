import difflib
import os
import subprocess
import sys

from collected_tests import CollectedTests
from config_tool import Config
from exceptions import RunException
from relative_path import RelativePath
from results import Results


class BasicRunner(RelativePath):
    def __init__(self):
        super().__init__()
        self._results = None

    def get_input_filename(self, offset=0):
        return self._get_filename(suffix='.input', offset=offset)

    def get_output_filename(self, offset=0):
        return self._get_filename(suffix='-answer', offset=offset)

    def get_expected_output_filename(self, offset=0):
        return self._get_filename(suffix='-expected', offset=offset)

    def get_filename_with_suffix(self, suffix, offset=0):
        return self._get_filename(suffix=suffix, offset=offset)

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
            print("Running command <<<", command, ">>>")
            p = subprocess.run(command, capture_output=True)
            print("Command output <<<", p.stdout.decode(), ">>>")
            print("Command error output <<<", p.stderr.decode(), ">>>")

        # print('XXXXXXXX', 'getting results')
        self._results = Results(use_expected_output=use_expected_output,
                                expected_output_filename=self.get_expected_output_filename(offset=1),
                                output_filename=self.get_output_filename(offset=1),
                                update_snapshot=update_snapshot,
                                strip_regex=strip_regex,
                                strip_keys=strip_keys,
                                strip_key_values_regex=strip_key_values_regex,
                                sort=sort)
        return self._results.get_and_update()

    @staticmethod
    def did_it_pass(name, expected, actual):
        class bcolors:
            FAIL = '\033[91m'
            ENDC = '\033[0m'

        if actual == expected:
            return True

        d = difflib.Differ()
        print(f"\n{bcolors.FAIL}{name} FAILED:{bcolors.ENDC}", file=sys.stderr)
        diff = d.compare(expected.split('\n'), actual.split('\n'))
        [print(f"{bcolors.FAIL}{x}{bcolors.ENDC}", file=sys.stderr) for x in diff]
        return False

    @staticmethod
    def assert_one_passed(names):
        passed = False
        has_misspelled_name = False
        print('Collected tests', CollectedTests.names)
        for name in names:
            collected, count = BasicRunner._was_collected(name)
            if Config.value.get(f'{name}_started', False):
                expected = Config.value.get(f'{name}_expected', '')
                actual = Config.value.get(f'{name}_actual', '')
                if not has_misspelled_name and BasicRunner.did_it_pass(f'{name}', expected, actual):
                    passed = True
            elif not collected:
                BasicRunner.did_it_pass(name,
                                        f'(test was amongst the {count} collected ones)',
                                        f'(test was NOT amongst the {count} collected ones)\n'
                                        f'(did you misspell its name?)')
                passed = False
                has_misspelled_name = True
        assert passed

    @staticmethod
    def _was_collected(name):
        return name in CollectedTests.names, len(CollectedTests.names)

    @staticmethod
    def get_all_props(class_name):
        return [class_name.__dict__.get(attr)
                for attr in dir(class_name)
                if not callable(getattr(class_name, attr))
                and not attr.startswith("__")]
