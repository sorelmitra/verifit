import pytest
import queue
from src import EndpointResult, EndpointResultConfig, EndpointResultComputer


@pytest.fixture
def setup_endpoint_result_computer():
	"""
	Sets up the EndpointResultComputer with a mock store and configuration.
	"""
	response_queue = queue.Queue()
	config = EndpointResultConfig(response_queue=response_queue, available_results=[],
								  success_status_code=200, status_code_after_fail=202)
	store = {EndpointResultConfig: config}
	computer = EndpointResultComputer(_store=store)
	return computer, config


def test_next_with_no_preconfigured_results(setup_endpoint_result_computer):
	computer, config = setup_endpoint_result_computer
	payload = {"data": "test"}
	result = computer.next(current_payload=payload)

	assert result.status_code == 200
	assert result.response_data == payload
	assert config.index == 1


def test_next_with_preconfigured_results_success(setup_endpoint_result_computer):
	computer, config = setup_endpoint_result_computer
	preconfigured_result = EndpointResult(status_code=201,
										  response_data={"preconfigured": True})
	config.available_results.append(preconfigured_result)

	result = computer.next(current_payload=None)

	assert result.status_code == 201
	assert result.response_data == {"preconfigured": True}
	assert config.index == 1


def test_all_preconfigured_results_fail(setup_endpoint_result_computer):
	computer, config = setup_endpoint_result_computer
	# Configure two failed results
	failed_results = [
		EndpointResult(status_code=404, response_data={"error": "Not Found"}),
		EndpointResult(status_code=500, response_data={"error": "Server Error"})
	]
	config.available_results.extend(failed_results)

	# First call, should fail with the first preconfigured result
	first_result = computer.next(current_payload=None)
	assert first_result.status_code == 404
	assert first_result.response_data == {"error": "Not Found"}
	assert config.did_previous_call_fail == True
	assert config.index == 1

	# Second call, should fail with the second preconfigured result
	second_result = computer.next(current_payload=None)
	assert second_result.status_code == 500
	assert second_result.response_data == {"error": "Server Error"}
	assert config.did_previous_call_fail == True  # Remains True after consecutive failures
	assert config.index == 2

	# Verify no more preconfigured results are available, and a default success response is generated
	default_result = computer.next(current_payload={"default": True})
	assert default_result.status_code == 202  # Default success-after-fail status
	assert default_result.response_data == {"default": True}
	assert config.index == 3  # Moved beyond preconfigured results


def test_next_with_failure_then_success(setup_endpoint_result_computer):
	computer, config = setup_endpoint_result_computer
	config.available_results.append(
		EndpointResult(status_code=404, response_data={"success": False}))
	config.available_results.append(
		EndpointResult(status_code=200, response_data={"success": True}))

	# First call, should fail
	first_result = computer.next(current_payload=None)
	assert first_result.status_code == 404
	assert first_result.response_data == {"success": False}
	assert config.did_previous_call_fail == True

	# Second call, should succeed but with altered status code due to previous failure
	second_result = computer.next(current_payload=None)
	assert second_result.status_code == config.status_code_after_fail
	assert second_result.response_data == {"success": True}
	assert config.index == 2
