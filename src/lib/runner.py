import json
import os
import traceback

from basic_runner import BasicRunner
from config_tool import Config
from graphql_tool import GraphQLTool
from websockets_tool import WebsocketsTool


class Runner(BasicRunner):
    def __init__(self):
        super().__init__()
        # When using the various filenames from this class,
        # we need to account for another function in the stack.
        self._local_stack_number = self._stack_number + 1
        self._old_stack_number = None
        self._old_filetype = None
        self._had_exception = None
        self._actual = None
        self._expected = None
        self._token = ''

    def cli(self,
            command,
            variables=None,
            check_token=None,
            use_expected_output=True,
            strip_regex=None,
            strip_keys=None,
            sort=None):
        self._prepare_for_test()

        if variables is not None:
            self._create_vars(self.get_input_filename(), variables)

        try:
            self._expected, self._actual = self.run(command=command,
                                                    use_expected_output=use_expected_output,
                                                    strip_regex=strip_regex,
                                                    strip_keys=strip_keys,
                                                    sort=sort)
        except Exception as e:
            self._handle_exception(e)
        finally:
            self._cleanup_after_test(check_token, use_expected_output)

        return self._expected, self._actual

    def login(self, path, username, password, check_token=None):
        return self.rest(path=path, method="POST",
                         use_input_file=False, use_expected_output=False,
                         input_data_raw={"username": username,
                                         "password": password},
                         use_token=False, check_token=check_token)

    def login_graphql(self, variables, check_token):
        return self.graphql(variables=variables,
                            use_token=False,
                            check_token=check_token,
                            use_expected_output=False)

    def rest(self,
             server=None,
             path='',
             method="GET",
             variables=None,
             filetype=None,
             use_token=True,
             check_token=None,
             use_input_file=True,
             input_data_raw=None,
             use_output_file=True,
             use_expected_output=True,
             retrieve_headers=False,
             follow_redirects=False,
             strip_regex=None,
             strip_keys=None,
             strip_key_values_regex=None,
             sort=None):
        self._prepare_for_test(filetype)

        if server is None:
            server = Config.value["REST_SERVER"]
        command = [
            "curl", "-X", method, f'{server}{path}',
            "--header", "Content-Type: application/json; charset=UTF-8",
        ]
        if use_token:
            command += [
                "--header", f"Authorization: Bearer {self._token}",
            ]
        if use_input_file:
            command += [
                "--data-binary", f"@{self.get_input_filename()}",
            ]
        if input_data_raw is not None:
            command += [
                "--data-binary", f"{json.dumps(input_data_raw)}",
            ]
        if use_output_file:
            command += [
                "--output", f"{self.get_output_filename()}",
            ]
        if retrieve_headers:
            command += [
                "--include",
            ]
        if follow_redirects:
            command += [
                "--location",
            ]

        if variables is not None:
            self._create_vars(self.get_input_filename(), variables)

        try:
            self._expected, self._actual = self.run(command=command,
                                                    use_expected_output=use_expected_output,
                                                    strip_regex=strip_regex,
                                                    strip_keys=strip_keys,
                                                    strip_key_values_regex=strip_key_values_regex,
                                                    sort=sort)
        except Exception as e:
            self._handle_exception(e)
        finally:
            self._cleanup_after_test(check_token, use_expected_output)

        return self._expected, self._actual

    def graphql(self,
                server_public=None,
                server_private=None,
                variables=None,
                use_token=True,
                check_token=None,
                use_expected_output=True,
                strip_regex=None,
                strip_keys=None,
                strip_key_values_regex=None,
                sort=None):
        self._prepare_for_test()

        gql_tool = GraphQLTool(
            server_public=server_public,
            server_private=server_private,
            input_filename=self.get_input_filename(),
            use_token=use_token,
            token=self._token)
        if variables is not None:
            self._create_vars(self.get_input_filename(), variables)
        command = gql_tool.prepare_query_and_command()

        try:
            self._expected, self._actual = self.run(command=command,
                                                    use_expected_output=use_expected_output,
                                                    strip_regex=strip_regex,
                                                    strip_keys=strip_keys,
                                                    strip_key_values_regex=strip_key_values_regex,
                                                    sort=sort)
        except Exception as e:
            self._handle_exception(e)
        finally:
            self._cleanup_after_test(check_token, use_expected_output)

        return self._expected, self._actual

    def websocket(self,
                  server=None,
                  variables=None,
                  check_token=None,
                  use_expected_output=True,
                  ignore_messages=None,
                  strip_regex=None,
                  strip_keys=None,
                  sort=None):
        self._prepare_for_test()

        if variables is not None:
            self._create_vars(self.get_input_filename(), variables)
        ws_tool = WebsocketsTool(server=server,
                                 input_filename=self.get_input_filename(),
                                 output_filename=self.get_output_filename(),
                                 ignore_list=ignore_messages)
        try:
            self._expected, self._actual = self.run(func=ws_tool.run,
                        use_expected_output=use_expected_output,
                        strip_regex=strip_regex,
                        strip_keys=strip_keys,
                        sort=sort)
        except Exception as e:
            self._handle_exception(e)
        finally:
            self._cleanup_after_test(check_token, use_expected_output)

        return self._expected, self._actual

    def get_stripped_values(self):
        return self._results.get_stripped_values()

    def _handle_exception(self, e):
        self._had_exception = True
        self._actual = e
        traceback.print_exc()

    def _prepare_for_test(self, filetype=None):
        self._old_filetype = self._data_file_type
        if filetype is not None:
            self._data_file_type = filetype
        self._old_stack_number = self._stack_number
        self._stack_number = self._local_stack_number
        self._expected, self._actual = "the test was run", "something happened"
        self._had_exception = False

    def _cleanup_after_test(self, check_token, use_expected_output):
        output_filename = self.get_output_filename()
        self._stack_number = self._old_stack_number
        self._data_file_type = self._old_filetype

        if self._had_exception:
            raise self._actual
        self._check_token(check_token)
        if not use_expected_output:
            os.unlink(output_filename)

    def _create_vars(self, input_filename, variables):
        filename_no_ext, _ = os.path.splitext(input_filename)
        vars_filename = f"{filename_no_ext}.vars.json"
        vars_template_filename = f"{filename_no_ext}.vars.template.json"
        with open(vars_template_filename) as f_vars_template:
            graphql_vars = f_vars_template.read()
            for key, value in variables.items():
                graphql_vars = graphql_vars.replace(f"${{{key}}}", value)
            with open(vars_filename, "wt") as f_vars:
                f_vars.write(graphql_vars)

    def _check_token(self, check_token):
        if check_token is None:
            return

        res = json.loads(self._actual)
        self._expected = "a token was returned (don't care about its value)"
        found = False
        for token_value in check_token:
            try:
                # print("XXXXXXXX", f"Checking if {token_value} is in {res}")
                properties = token_value.split('.')
                for prop in properties:
                    res = res[prop]
                self._token = res
                self._actual = self._expected
                found = True
            except KeyError:
                pass
        if not found:
            self._actual = f"no token was returned"


runner = Runner()
