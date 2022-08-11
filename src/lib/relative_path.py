import inspect
import os


class RelativePath:
    def __init__(self):
        self._stack_number = 1
        self._stack_file_index = 1
        self._stack_function_index = 3
        self._data_file_type = 'json'

    def _get_filename(self, suffix='', offset=0):
        offset = offset + 1
        name = inspect.stack()[self._stack_number + offset][self._stack_function_index]
        # print('XXXXXXXX', '_get_filename', 'suffix', suffix)
        return self.script_path(f"{name}{suffix}.{self._data_file_type}", offset=offset)

    def script_path(self, filename, offset=0):
        # Have tried several ways to get this path, including hardcoded and:
        # dir = sys.path[0] # uses Python Path entries - not reliable.
        #
        # The solution I chose is based on reflection.
        # First index is stack function, second index is file name.
        # Partially reliable, works only if
        # - this function is called from within another function from this class,
        #   which in turn is called directly from the test file.
        # Best solution I have so far.

        # for i in range(0, len(inspect.stack())):
        #     print('XXXXXXXX', 'frame', i, inspect.stack()[i])
        stack_number = self._stack_number + offset + 1
        # print('XXXXXXXX', 'stack_number', stack_number, self._stack_number)
        current_dir = os.path.dirname(inspect.stack()[stack_number][self._stack_file_index])
        return os.path.join(current_dir, filename)
