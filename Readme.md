
# Authentication Tools Library

This small Python library provides a few tools designed to facilitate the writing of automated tests for any type of application. It encompasses functionalities for login procedures, a caching mechanism for efficient data retrieval, a utility for simulating successful and failed communication results, and a few operations for date and time calculations. The library aims to streamline authentication tasks, improve performance via caching strategies, and assist with testing apps that depend on other services or APIs.


# Project Structure

The project is organized into two main directories, `src` for the source code and `test` for the self-test suite, ensuring the functionality is thoroughly verified.

## Source Code (`src`)

The `src` directory encapsulates the core functionalities divided into several modules:

- **`endpoint_tools.py`**: Manages endpoint results, including checks for success and configuration for sequences of endpoint results. By 'endpoint' we really mean any type of communication from your app to some other service that returns a payload and some status code. So with this library you're not tied to a particular type of service or API.

- **`cache.py`**: Provides caching functionalities to store, retrieve, and manage any type of JSON-serializable data, enhancing performance and data retrieval efficiency.

- **`json_web_token.py`**: Facilitates operations related to JWTs, such as decoding and extracting expiration dates, used in the cache mechanism.

- **`date_tools.py`**: Contains utilities for date and time calculations, supporting operations like token expiration checks.

- **`login.py`**: Handles login operations, leveraging JWT validation and caching for optimized login processes. The module only does the bookkeeping around logging in. The actual log in is done by the user of the library, via a very simple `driver` mechanism - you need to supply a function that takes a username and secret, and returns an access token as a JWT string. So, apart from JTW, this library is not tied to any particular authentication mechanism.

Each module is documented inline, offering insights into their functionalities and usage.

## Tests (`test`)

The `test` directory includes tests for the source code's functionality, structured as follows:

- **`test_login.py`**: Ensures the login process, including token handling and caching, works as expected under various scenarios.

- **`test_endpoint_tools.py`**: Verifies the endpoint results simulation, with both success and failure cases.

Tests are implemented with `pytest`, which is a robust framework for validating each component's correctness and reliability.


# Conclusion

This library went through quite a few iterations.  Its present form reflects my current stance on helper libraries in general: In-house developed libraries should be kept as simple and focused as possible.  Large project templates or frameworks actually make things worse in both the long and short term, because of the time they consume for writing and maintaining them on one side, and on understanding and using them, on the other.
