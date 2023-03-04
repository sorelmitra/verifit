#!/bin/sh

start_time=$(date +%s)

# POSIX way of getting current script's directory
a="/$0"; a="${a%/*}"; a="${a:-.}"; a="${a##/}/"; script_dir=$(cd "$a" || return 234; pwd)

lib_subdir="../lib/shell"
local_lib_subdir="lib/local/shell"
lib_dir="${script_dir}/${lib_subdir}"
local_lib_dir="${script_dir}/${local_lib_subdir}"
# ShellCheck does not expand variables
# shellcheck source=lib/shell/lib.sh
. "${lib_dir}/lib.sh"


environments="dev"
drivers="post-service-1,post-service-2"

usage_exit() {
	echo "Usage: $(basename -- "$0") -e <environment> [-d '<driver>' ...] [-f <pytest filter>]"
	echo "  Run End-to-End (E2E) tests with the following settings:"
	echo "  <environment>: Environment where to run the tests, one of <${environments}>"
	echo "  <driver>: Driver to use when running tests, one of <${drivers}>"
	echo "            Can be specified multiple times in order to run with multiple drivers"
	echo "            If none is specified, then it runs with all drivers"
	echo "  <pytest filter>: Tests filter, it is passed on to pytest"
	echo
	echo "$1"
	exit 1
}

driver=""
while getopts 'e:d:f:' OPTION; do
	case $OPTION in
	e)
		environment=${OPTARG}
		;;
	d)
	  add_to_driver "${OPTARG}"
		;;
	f)
		filter=${OPTARG}
		;;
	?)
		usage_exit ""
		exit 2
		;;
	esac
done

if [ -z "${environment}" ]; then usage_exit "Missing environment!"; fi
if [ -z "${driver}" ]; then driver="${drivers}"; fi

test_group_name="Post-Service"
header1 "${test_group_name}"
get_wording_based_on_column_count ${driver} "driver" "drivers"
# shellcheck disable=SC2154
echo "Running ${bold_on}${test_group_name}${normal_text} E2E tests suites in environment ${bold_on}${environment}${normal_text}, with ${wording} ${bold_on}${driver}${normal_text}"

# shellcheck disable=SC2034
csv_row=${driver}
# shellcheck disable=SC2034
csv_column=0
driver_index=0
# shellcheck disable=SC2154
while [ "$driver_index" -le "$((csv_column_count-1))" ]; do
  csv_get_next_column
  driver_index=$((driver_index+1))
  header2 "Running test suite for driver ${csv_value}"
  ENV=${environment} TENANT=${tenant} FILTER=${filter} "${local_lib_dir}/run-${csv_value}.sh"
  compute_suite_result
done

end_time=$(date +%s)
compute_and_report "${start_time}" "${end_time}" "${test_group_name}"
