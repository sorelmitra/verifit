import copy
import json
import os
import re
from shutil import copyfile

from exceptions import *


class Results:
    def __init__(self,
                 use_expected_output=False,
                 expected_output_filename=None,
                 output_filename=None,
                 update_snapshot=None,
                 strip_regex=None,
                 strip_keys=None,
                 sort=None):
        self._use_expected_output = use_expected_output
        self._expected_output_filename = expected_output_filename
        self._output_filename = output_filename
        self._update_snapshot = update_snapshot
        self._strip_regex = strip_regex
        self._strip_keys = strip_keys
        self._sort = sort
        self._stripped_values = []

    def get_and_update(self):
        actual = self._load_file_as_string(self._output_filename, should_format=True)
        self._update_output_file_content(actual)
        self._maybe_update_snapshot()
        expected = None
        if self._use_expected_output:
            expected = self._load_file_as_string(self._expected_output_filename)
        return expected, actual

    def get_stripped_values(self):
        return self._stripped_values

    def _load_file_as_string(self, filepath, should_format=False):
        with open(filepath) as f:
            content = f.read()
        if self._strip_regex is not None:
            content = self._do_strip_regex(content)
        if should_format and len(content) > 1:
            try:
                dict_content = json.loads(content)
                if self._sort is not None:
                    dict_content = self._sort_dict_lists(filepath, dict_content)
                if self._strip_keys is not None:
                    dict_content = self._do_strip_keys(dict_content)
                formatted_content = json.dumps(dict_content, indent=2)
                content = formatted_content
            except RunException as e:
                raise e
            except json.decoder.JSONDecodeError:
                pass
        return content

    def _sort_dict_lists(self, filepath, dict_content):
        sorted_dict = copy.deepcopy(dict_content)
        for list_dict in self._sort:
            # print("XXXXXXXX", 1, list_dict)
            list_name = list_dict['list']
            field = list_dict['field']
            keys = list_name.split('.')
            # print("XXXXXXXX", 2, "field", field, "keys", keys)
            inner_dict = sorted_dict
            key = None
            i = None
            for i in range(len(keys) - 1):
                # print("XXXXXXXX", '2b', i)
                key = keys[i]
                try:
                    inner_dict = inner_dict.get(key)
                    # print("XXXXXXXX", 3, "key", key, "inner_dict", inner_dict)
                except KeyError:
                    # print("XXXXXXXX", 4, key)
                    raise RunException(f"Could not find list {list_name} in {filepath}: missing key <{key}>")
            if i is not None:
                key = keys[i + 1]
            try:
                # print("XXXXXXXX", 5, "key", key, "inner_dict", inner_dict)
                if key is None:
                    inner_dict = sorted(inner_dict, key=lambda x: x[field])
                    sorted_dict = inner_dict
                else:
                    inner_dict[key] = sorted(inner_dict[key], key=lambda x: x[field])
                # print("XXXXXXXX", 6, "inner_dict", inner_dict)
            except KeyError:
                raise RunException(f"Could not sort list {list_name} in {filepath}: missing field <{field}> in list")
        # print("XXXXXXXX", 8, sorted_dict)
        return sorted_dict

    def _do_strip_regex(self, content):
        for regex in self._strip_regex:
            content = re.sub(regex, '', content)
        return content

    def _do_strip_keys(self, dict_content):
        self._stripped_values = []
        # print("XXXXXXXX", 1, strip_keys)
        for compound_key in self._strip_keys:
            keys = compound_key.split('.')
            # print("XXXXXXXX", 2, keys)
            inner_dict = dict_content
            i = None
            for i in range(len(keys) - 1):
                key = keys[i]
                inner_dict = inner_dict.get_and_update(key)
            if i is None:
                last_key = keys[0]
            else:
                last_key = keys[i + 1]
            # print("XXXXXXXX", 3, last_key)
            self._stripped_values.append(inner_dict[last_key])
            del inner_dict[last_key]
            # print("XXXXXXXX", 4, stripped_values)
        return dict_content

    def _update_output_file_content(self, content):
        with open(self._output_filename, "wt") as f:
            f.write(content)

    def _maybe_update_snapshot(self):
        if not self._should_update_snapshot():
            return
        _, ext = os.path.splitext(self._output_filename)
        copyfile(self._output_filename, self._expected_output_filename)

    def _should_update_snapshot(self):
        print("should_update_snapshot", self._update_snapshot)
        if self._update_snapshot:
            return True
        try:
            return os.environ["UPDATE_SNAPSHOT"]
        except KeyError:
            return False
