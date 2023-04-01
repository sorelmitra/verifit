# About

This is a Python library aimed at developers, that simplifies setting up and using automatic system testing for several types of projects.

I've named it `verifit` as a contraction of `Verify It!`, i.e. "Make sure your system works fine!"



# Introduction

## Why Developer-Based Automatic System Testing?

Automatic system (or application-level) testing done by developers is a must for every project.  Even if you have a dedicated QA team, automatic system testing is a very valuable tool for making sure your product works as expected:

- It allows developers to be very confident of the quality of the products that they ship.
- Sometimes you can't test a system 100% automatically. But, if you manage to cover the functionality (and perhaps some non-functional requirements, such as performance and high-availability - depending on the nature of the project), this will be a big help as the project builds up, and the risk of breaking something increases.
- It makes bug investigation easier - if you know the case covered by the bug passes in your automated tests, then the source must be elsewhere, such as misconfiguration or wrong parameter.
- It makes QA team's life easier by helping them design their tests.

## Why This Libray?

For the above to work, though, the developers must be maintaining their tests along with the code base, or even better, do TDD.

This library aims to make a developer's life easier by leveraging the already very friendly PyTest tool, and building upon it with a handful of commonly used options, such as environment variables or making authorized HTTPS requests.

Also, on small projects or where you're time constrained, having an automatic system testing framework that's easy to put to use on a daily basis is of great help.

## Side Note: Black Box Testing

There are multiple ways of writing automated tests, and this library is not tied to any particular methodology.

However, one particular testing methodology I favor is **black box testing**, in which you treat your system as a black box, and *never check its internals*.  I find it has quite a few advantages, and I thought I'd list some of them here:

- Easy to put in place.  You just hit your system in the same way its clients would.  No need to write code that checks databases, Kafka, or who knows what.
- Can serve as acceptance testing.  You can put up compound scenarios.
- It's resistant to system implementation changes.




# Overview

This library supports any type of tests that can be done with PyTest, and note that this is by no means limited to Python projects.

You can have your automatic developer testing done in a different language than your project's.  PyTest is my go-to stack for automatic testing, in the absence of constraints imposed by the project I'm working on.

Normally, if you're using PyTest and a few other standard Python modules, you can test pretty much anything quite fast, without needing a library.  However, as you start doing this, you soon realize you're going to need some things over and over again in your tests.  This small library provides a few helpers for making a developer's automatic testing easier:

- Quick configuration.
- A cache for speeding up things such as getting access tokens, or any other data that is reused.
- A quick way to do driver-based testing, in which the test case relies on a particular driver (specified at runtime)  that does the action and returns the result.  This allows you to run the same test against different drivers, such as an API, UI, etc.
- Simplified mechanism for skipping tests that are not suitable for a particular driver.
- Web-Sockets testing.  (I couldn't find a Python package that makes testing Web-Sockets as easy as calling a couple of functions.)
- Some other helper tools, like date, JWT, etc.

This repo consists of the actual library, which is in `src/verifit/`, and some sample tests from which you can inspire when writing your own.


# Quick Start with Writing Tests

## 1. Install Required Libraries

- Install Python 3.6 or higher.
- Install PyTest.
- Copy the [requirements from the sample tests](https://github.com/sorelmitra/verifit/blob/main/tests/requirements.txt) to your PyTest project.  Adjust them to suit your needs, and then install them.

## 2. Read the Sample Tests & Configs

We have a `tests/` directory that shows how to use this library. Please make sure to read this section while browsing that folder. It will get you started real quick.

### 2.1. Sample Configs

The following configs are made in order to run the sample tests:

- `requirements.txt`: Lists `verifit`, as well as other packages used by it or by our sample tests.
- `pytest.ini`: Defines `skip_drivers`, which is a marker that allows skipping drivers easily.
- `conftest.py`: Defines fixtures that allow selecting the current driver by name, from a list of drivers provided by each test.
- `login_before_test.py`: Defines login helper functions for tests that require this.
- `.dev.env`: Hosts configuration for our drivers, such as endpoints or users.

### 2.2. Sample Tests

The sample tests use dummy online services to prove usage of our lib: 

1. `post_service/post/test_post.py`. Tests the same action using HTTP and GraphQL servers. The test is based on drivers for calling to the different servers. We also use `skip_drivers` to ignore a test for a particular driver.

2. `shopping_service/login/test_login.py`. Here we test log in to a server using drivers.

3. `shopping_service/login/test_products.py`. This one does the following:

   - Logs in from cache using `login_before_test.py`.
   - Calls to a private endpoint, using drivers. It requests authorization by using the access token obtained when logged in.

4. `shopping_service/login/test_carts.py`. It shows combining Gherkin features and BDD with drivers.

5. `echo_service/test_echo_service.py`.  Shows how to simplify testing WebSockets using our library.

6. `date_service/test_date.py`.  Shows how to test CLI programs using this lib: it runs the shell command `date` with some arguments, and verifies the resulting output.

7. `cache/test_cache.py`.  Tests our cache mechanism.

8. `kitchen_service/test_kitchen_service.py`.  Showcase doing a Web UI test using Cypress.IO and their kitchen sink sample page.

To run all sample test suites included with this project, do this:

```shell
cd tests
pip install -r requirements.txt
pytest .
```

Selecting which tests to run:

- Run only tests that are related to posts and shopping: `pytest . -k 'post_service or shopping_service'`.
- Run the posts tests only with the first driver: `POST_DRIVER='bar' pytest . -k 'post_service'`.
- Run the posts tests with multiple drivers explicitly set: `POST_DRIVER='bar,baz' pytest . -k 'post_service'`.

## 3. Write Some Tests

Using the sample configs and tests as an inspiration, go ahead and write and run your own!




# Reference

The entire library is coded using Functional Programming principles.  Thus, you will see:

- Pure functions, that return the same result given the same input, and that do not have side effects.
- Immutability & disciplined state - functions do not alter state outside them, and there's no shared state between functions.
- Currying - at most one argument for each function.
- Higher-order functions - that return another function.
- The memoize pattern used to make sure a single instance of a thing exists (in our case the config store).
- No global variables, not even a singleton - memoize takes care of this.

## Helpers

- `cache.py`.  Implements a simple cache, stored in `<tests>/.<env>-cache.json` 
- `config.py`.  Loads configuration via `dotenv` package, and returns a memoized store for getting/setting values across tests.
- `date_diff.py`.  Simple date diff.
- `driver.py`.  This one provides a few utilities:
  * `select_driver` selects a driver function based on name, from a list of function objects that you provide.  It expects the names of the function objects to follow the pattern `driver.+{driver_name}`.  It returns the found function, or raises an exception if it fails to find one.  **Note** that if you have a driver named `bar` and another driver named `foo_bar`, this function will throw an exception because it cannot differentiate between the two.
  * `get_driver_params` returns the driver names as defined either in an environment variable, either by a default list of names.
  * `get_driver_name` returns the current driver name as injected by PyTest from the driver names returned by `get_driver_params`.
- `json_web_token.py`.  Decoding and extracting data from a JWT.
- `login.py`.  Functions to:
    - Log in using the provided driver.
    - Log in from a cached token.
    - Building authorization values:
      - For HTTP headers.
      - For the Python GraphQL client.
- `memoize.py`.  Simple memoize pattern, used by `config.py` to provide a single store instance for sharing data across tests.
- `prop.py`: Access dictionary properties without exceptions and with default values.
- `retrieve.py`. Shortcut functions for calling to HTTP or GraphQL endpoints, with unified logging.
- `web_sockets.py`.  Simplifies Web-Sockets testing by offering functions for listening in background for received packages, and sending data.




# Development

## Library

If you want to develop, build, and upload this library to PyPI, do this:

First, set up a few things:

- Install Python 3.6 or higher.
- Install the requirements from `requirements.txt`.

The lib code is in `src/verifit`.  Make sure to use proper `.` imports to avoid importing from the installed `verifit` library accidentally.

Once your code changes are ready and documented, do the following to upload:

1. Commit everything to GIT.

2. Check Manifest. Run:

   ```shell
   check-manifest
   ```

3. Increase the version in `pyproject.toml`:

   ```toml
   [project]
   version = "X.Y.Z"
   ```

4. Increase the minimum version in `tests/requirements.txt`:

   ```
   verifit >= X.Y.Z
   ```

5. Build package. Run:

   ```shell
   python -m build
   ```

6. Check build. Run:

   ```shell
   twine check dist/verifit-X.Y.Z*
   ```

7. Upload to Test.PyPI. Run:

   ```shell
   twine upload -r testpypi dist/verifit-X.Y.Z*
   ```

8. Install manually from Test.PyPI. Run:

   ```shell
   pip install -i https://test.pypi.org/simple verifit==X.Y.Z
   ```
    (First time it may fail, in this case, rerun the above command.)

9. Run the sample tests:

   ```shell
   cd tests/ && pytest .
   ```

10. If everything goes well, upload to PyPI. Run:

   ```shell
   twine upload dist/verifit-X.Y.Z*
   ```

11. Install sample tests requirements. Run:

   ```shell
   cd tests/ && pip install -r requirements.txt
   ```
    (First time it may fail, in this case, rerun the above command.)

12. Run the sample tests again:

   ```shell
   cd tests/ && pytest .
   ```
    If all went well, they should pass.

13. You can now push to GIT.

## Sample Tests

Setup:

- Go to `tests/kitchen_service/ui` and run `yarn install`.
- Install sample tests requirements. Run:

   ```shell
   cd tests/ && pip install -r requirements.txt
   ```
Change tests code, then make sure to test, document, & push your changes.
