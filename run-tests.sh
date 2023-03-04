#!/bin/sh

start_time=$(date +%s)

# POSIX way of getting current script's directory
a="/$0"; a="${a%/*}"; a="${a:-.}"; a="${a##/}/"; script_dir=$(cd "$a" || return 234; pwd)

lib_subdir="lib/shell"
lib_dir="${script_dir}/${lib_subdir}"
# ShellCheck does not expand variables
# shellcheck source=lib/shell/lib.sh
. "${lib_dir}/lib.sh"

environments="dev"

usage_exit() {
	echo "Usage: $(basename -- "$0") -e <environment> [-f <pytest filter>]"
	echo "  Run End-to-End (E2E) tests with the following settings:"
	echo "  <environment>: Environment where to run the tests, one of <${environments}>"
	echo "  <pytest filter>: Tests filter, it is passed on to pytest"
	echo
	echo "$1"
	exit 1
}

while getopts 'e:d:f:' OPTION; do
	case $OPTION in
	e)
		environment=${OPTARG}
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

echo
# shellcheck disable=SC2154
echo "Running E2E tests groups in environment ${bold_on}${environment}${normal_text}"

ENV=dev pytest --collect-only ./post-service -k "${filter}" | grep 'no tests collected' >/dev/null
res=$?
if [ "${res}" -eq 0 ]; then
  title " Post-Service Test Group "
  # shellcheck disable=SC2154
  echo "${yellow_on}SKIPPED${normal_text}"
else
  title " Post-Service Test Group "
  "${script_dir}"/post-service/run-post-service-tests.sh -e "${environment}" -f "${filter}"
  compute_suite_result
fi

title " Everything else Test Group"
if [ -n "${filter}" ]; then
  ENV=${environment} pytest echo-service -k "${filter}"
else
  ENV=${environment} pytest echo-service
fi
compute_suite_result

end_time=$(date +%s)
compute_and_report "${start_time}" "${end_time}"
