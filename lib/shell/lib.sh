bold_on=$(tput bold)
# shellcheck disable=SC2034
green_on="\033[32m"
# shellcheck disable=SC2034
red_on="\033[91m"
# shellcheck disable=SC2034
yellow_on="\033[33m"
# shellcheck disable=SC2034
color_off="\033[0m"
normal_text=$(tput sgr0)


lines_before_count=5
separator_lines_count=2
lines_after_count=2
message=""
message_fill_char="-"
print_title_message() {
  message_len=$(echo "${message}" | wc -m | awk '{print $1}')
  terminal_cols=$(tput cols)
  terminal_cols=$(( terminal_cols - 1 ))
  fill_len=$(( terminal_cols - message_len ))
  fill_rest=$(( fill_len % 2 ))
  fill_half_1_len=$(( fill_len / 2 + fill_rest ))
  fill_half_2_len=$(( fill_len / 2 ))
  #echo "cols=${terminal_cols} len=${message_len} fill_len=${fill_len} fill_rest=${fill_rest} half_fill_1=${fill_half_1_len} half_fill_2=${fill_half_2_len} all_fill=$((fill_half_1_len * 2))"
  i=0; while [ $i -le $lines_before_count ]; do echo; i=$((i+1)); done
  j=0; while [ $j -le $((separator_lines_count-1)) ]; do
    i=0; while [ $i -le $terminal_cols ]; do printf %s "${message_fill_char}"; i=$((i+1)); done
    j=$((j+1))
  done
  i=0; while [ $i -le $fill_half_1_len ]; do printf %s "${message_fill_char}"; i=$((i+1)); done
  printf %s "${bold_on}${message}${normal_text}"
  i=0; while [ $i -le $fill_half_2_len ]; do printf %s "${message_fill_char}"; i=$((i+1)); done
  i=0; while [ $i -le $lines_after_count ]; do echo; i=$((i+1)); done
}

title() {
	lines_before_count=15
	separator_lines_count=6
	lines_after_count=5
	message="$1"
	print_title_message
}

h1_nr=0
h2_nr=0
header1() {
	h1_nr=$((h1_nr+1))
	h2_nr=0
	lines_before_count=10
	separator_lines_count=4
	lines_after_count=2
	message=" $h1_nr. $1 "
	print_title_message
}

header2() {
	h2_nr=$((h2_nr+1))
	lines_before_count=5
	separator_lines_count=2
	lines_after_count=1
	message=" $h1_nr.$h2_nr. $1 "
	print_title_message
}


csv_row=""
csv_column=0
csv_value=""
csv_get_next_column() {
  csv_column=$((csv_column+1))
  csv_value=$(echo "${csv_row}" | awk -F ',' '{print $'$csv_column'}')
}

csv_column_count=0
csv_get_column_count() {
  while 'true'; do
    csv_get_next_column
    if [ -z "${csv_value}" ]; then break; fi
		csv_column_count=$((csv_column_count+1))
  done
}


driver=""
add_to_driver() {
  arg_to_add=$1
  if [ -z "${driver}" ]; then
    driver_prev=""
  else
    driver_prev="${driver},"
  fi
  driver="${driver_prev}${arg_to_add}"
}


wording=""
get_wording_based_on_column_count() {
  csv_row="${1}"
  singular="${2}"
  plural="${3}"
  csv_column=0
  csv_get_column_count
  if [ "$csv_column_count" -ge 2 ]; then
    wording=${plural}
  else
    # shellcheck disable=SC2034
    wording=${singular}
  fi
}


passed_suites=0
failed_suites=0
total_suites=0
compute_suite_result() {
  run_result=$?
  total_suites=$((total_suites+1))
  if [ "$run_result" -eq 0 ]; then
    passed_suites=$((passed_suites+1))
  else
    failed_suites=$((failed_suites+1))
  fi
}


compute_and_report() {
  start_time="$1"
  end_time="$2"
  test_group_name="$3"
  total_time_seconds=$(( end_time - start_time ))
  total_time_minutes=$(( total_time_seconds / 60 ))
  total_time_hours=$(( total_time_minutes / 60 ))
  total_time_minutes=$(( total_time_minutes % 60 ))
  total_time_seconds=$(( total_time_seconds % 60 ))
  total_time=$(printf '%02d:%02d:%02d' "${total_time_hours}" "${total_time_minutes}" "${total_time_seconds}")
  if [ "${total_suites}" -ge 2 ]; then suite_or_group_wording="suites"; else suite_or_group_wording="suite"; fi
  if [ "${passed_suites}" -le 0 ]; then
    passed_suites_color="${red_on}"
  else
    passed_suites_color="${green_on}"
  fi
  if [ "${failed_suites}" -ge 1 ]; then
    failed_suites_color="${red_on}"
  else
    failed_suites_color="${green_on}"
  fi
  test_group_name_wording="Executed"
  if [ -n "${test_group_name}" ]; then
    echo
    echo
    test_group_name_wording="${test_group_name},"
  else
    title ""
    if [ "${total_suites}" -ge 2 ]; then suite_or_group_wording="groups"; else suite_or_group_wording="group"; fi
  fi
  echo "${test_group_name_wording} ${bold_on}${total_suites} E2E test ${suite_or_group_wording}${normal_text}: ${passed_suites_color}${passed_suites} passed${color_off}, ${failed_suites_color}${failed_suites} failed${color_off} in ${total_time}"
  echo
  echo
  if [ "$failed_suites" -ge 1 ]; then
    exit 1
  fi
}
