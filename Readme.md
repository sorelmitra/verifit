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

You can by all means have your automatic developer testing done in a different language than your project's.  PyTest is my go-to stack for automatic testing, in the absence of constraints imposed by the project I'm working on.

Normally, if you're using PyTest and a few other standard Python modules, you can test pretty much anything quite fast, without needing a library.  However, as you start doing this, you soon realize you're going to need some things over and over again in your tests.  This small library provides a few helpers for making a developer's automatic testing easier:

- Quick configuration.
- A cache for speeding up things such as getting access tokens, or any other data that is reused.
- A quick way to do driver-based testing, in which the test case relies on a particular driver (specified at runtime)  that does the action and returns the result.  This allows you to run the same test against different drivers, such as an API, UI, etc.
- Simplified mechanism for skipping tests that are not suitable for a particular driver.
- Web-Sockets testing.  (I couldn't find a Python package that makes testing Web-Sockets as easy as calling a couple of functions.)
- Some other helper tools, like date & time, etc.

This repo consists of the actual library, which is in `lib/`, and some sample tests from which you can inspire when writing your own.


# Quick Start with Writing Tests

## 1. Install Required Libraries

- Install Python 3.6 or higher.
- Install PyTest.
- Copy the [requirements from the sample tests](https://github.com/sorelmitra/verifit/blob/main/tests/requirements.txt) to your PyTest project and install them.  This will basically install the `verifit` library to its latest stable version, along with all other requirements for these particular tests.

## 2. Prepare a ConfTest File with Driver Names

**Note 1**: You can skip this section if you're not going to use drivers in your tests.

**Note 2**: The Post-Service and Shopping-Service sample tests use drivers.  For more details, check our [drivers reference](#drivers) section below.

Let's assume you have two services, `my-service`, and `my-second-service`, and each one of them has different needs for a driver:

- `my-service` has a REST, GraphQL, and UI interface, and you want to test them all, ideally without duplicating test cases.  The use cases for all interfaces are similar, and you want to reuse your test cases.
- `my-second-service` has multiple versions, and most of your tests apply to all of them, so again  you want to reuse them.

To achieve this with this library, add the following code into your `conftest.py` file:

```python
import pytest

from src.lib.driver import get_driver_params, get_driver_name


@pytest.fixture(params=get_driver_params('MY_DRIVER')(['my-service-rest', 'my-service-graphql', 'my-service-ui']))
def my_driver_name(request):
    return get_driver_name(request)


@pytest.fixture(params=get_driver_params('MY_SECOND_DRIVER')(['my-second-service-v1', 'my-second-service-v2', 'my-second-service-v3', 'my-second-service-v4']))
def my_second_driver_name(request):
    return get_driver_name(request)
```

(In the rest of this section, we focus on `my-service`.  The same pattern applies for `my-second-service`.)

Then in your test file, use the driver like this:

```python
from verifit.driver import get_driver
def test_stuff(my_driver_name):
   data = {}  # the data that <do-stuff> needs
   get_driver(my_driver_name)('do-stuff')(data)
```

Now the framework will make sure to call `do-stuff` for each driver that is specified in the environment variable `MY_DRIVER`, or by default for the list declared in the fixture: `['my-service-rest', 'my-service-graphql', 'my-service-ui']`.  Specifically, it will look for Python files named like this, in any folder known to PyTest **(*)**:

- `my-service-rest_do-stuff.py`: Do stuff via REST.
- `my-service-graphql_do-stuff.py`: Do stuff via GraphQL.
- `my-service-ui_do-stuff.py`: Do stuff via UI.

**(*)** **Note**: For this to work, though, you need that other folder to have **at least** one `test_...` function that Py.Test collects, otherwise it will not be in the path and it will fail to find your driver.

Inside each Python file, it will expect to find an `execute()` function, which it will load and return as a first-class object.  Note that the `execute()` function is not being called by the framework.

If you need to specify `MY_DRIVER`, do it like this: `MY_DRIVER='my-service-rest,my-service-ui' pytest my-tests`.  This will run your tests for only the REST and UI drivers.

In case a particular test does not make sense for particular drivers, mark it as such with:

```python
@pytest.mark.skip_drivers([
    {'name': 'my-service-ui', 'reason': 'Not implemented yet'}
])
def test_another_stuff(my_driver_name):
   data = {}  # the data that <do-another-stuff> needs
   get_driver(my_driver_name)('do-another-stuff')(data)
```

Now the framework will skip `test_another_stuff` if the driver is for UI, and instruct PyTest to display the given reason.  You can specify multiple drivers for which a test is to be skipped.  The name is mandatory.  If a reason is not specified, it will display a default reason.

## 3. Inspire from the Sample Tests 

We have a bunch of test suites that you can inspire from.  Each suite tests an imaginary service, which is either an online dummy one, either a dummy shell command. 

1. **Post-Service**.  This one can "post" to a particular server via a driver.  Each driver connects to the server it can talk to, and makes sure the returned data has the same format in order for the test to function.  Here we showcase:
   - Using multiple drivers:
      - `post-service-1` that connects to a REST API.
      - `post-service-2` that connects to a GraphQL API.
   - Ignoring a test for a particular driver, namely `test_post_second`.
2. **Echo-Service**.  It sends a message to a Web-Sockets server and gives back the response.  In our case, the dummy WSS server echoes back whatever we're sending, so the test verifies this.
3. **Shopping-Service**.  This test shows multiple features:
   - Login and get an access token.  (`test_login.py`)
   - Accessing an authorized endpoint with an access token.  (`test_products.py`)
   - Caching some values, in this case the access token for a particular user.  (`test_login.py`)
   - Log in from cache, which means reusing the cached access token if it's not close to expiration date.  If no suitable token is found, log in again.  (`test_products.py`)
   - BDD using `pytest-bdd` and Gherkin.  Implements a similar test to `test_products.py`, but this time with a Gherkin feature file and `@given`, `@when`, `@then`.  Showcases matching a Gherkin declaration with regular expressions.  (`test_carts.py`)
4. **Date-Service**.  It runs the shell command `date` with some arguments, and verifies the resulting output.
5. **Kitchen-Service**.  Web UI test using Cypress.IO and their kitchen sink sample page.  It is called from a Python test that runs Cypress via `subprocess`.

To run all sample test suites included with this project, do this:

```shell
cd tests
pip install -r requirements.txt
pytest .
```

Selecting which tests to run:

- Run only tests that are related to posts and shopping: `pytest post-service shopping-service`.
- Run the posts tests only with the first driver: `POST_DRIVER='post-service-1' pytest post-service`.
- Run the posts tests with multiple drivers explicitly set: `POST_DRIVER='post-service-1,post-service-2' pytest post-service`.

## 4. Write Some Tests

You can now start writing tests!  (Perhaps by copying one of the samples.)

## 5. Run Tests

Run your tests as usual, by invoking `pytest`, specifying the environment name, and driver, if that's the case, and any other environment variables you might need in your tests.

E.g., assuming you have:

- The drivers presented in the section on [preparing drivers](#2-prepare-a-conftestpy-file-with-drivers) above.
- The environment `sandbox`.
- A tenant-based app.
- The tenant `dev-test` set up for testing.
- All your tests in the `tests/` folder,

then you could run your tests for REST and UI like this:

```shell
ENV=sandbox tenant=dev-test MY_DRIVER='my-service-rest,my-service-ui' pytest tests
```



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
- `date_and_time.py`.  Some simple date/time utils, such as a diff.
- `driver.py`.  Imports a driver function that you define, based on a driver name and functionality name.  It allows you to:
    - Quickly define PyTest fixtures that gives you the driver name based on [fixture parameterizing](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#fixture-parametrize).
    - Call a driver by name and functionality, with parameters.
- `iam_token.py`.  Decoding and extracting data from a JWT.
- `login.py`.  Functions to:
    - Log in, including by using a cached token.
    - Building authorization values:
      - For HTTP headers.
      - For the Python GraphQL client.
- `memoize.py`.  Simple memoize pattern, used by `config.py`.
- `web_sockets.py`.  Simplifies Web-Sockets testing by offering simple functions for listening in background for received packages, and sending data.

## Drivers

We have already shown a few practical steps for how to use drivers, in the above section for [preparing drivers](#2-prepare-a-conftest-file-with-driver-names).

Here, we go into more details on how this works.  We explain how the sample shopping test & driver are implemented, with respect to login.

Side note on drivers & PyTest:

- The driver mechanism is tied to PyTest parameterized fixtures, because they fit our purpose nicely, allowing you to select your drivers at runtime, as well as providing defaults.
- Also, if we wanted to implement our own mechanism for driver-based testing, independent of a test runner, things would've got much more complicated, as we:
    - Would reinvent the wheel and write a lot of code to duplicate functionality that's common in test runners.
    - Would require you to run the tests in awkward ways, by wrapping test runner commands in scripts we would provide.
- Thus, we chose not to take this path, and instead coach you on how to use PyTest in order to achieve this.  We do provide the most important functionality, however, which is finding and importing the driver code.

So we want to log in from the tests to our shopping service using the endpoint that the latter offers.  For now, we only have one endpoint for this, but assuming we later might add another one, or that we will be adding UI on top of this, we want to use drivers in order to have the flexibility of using the new endpoint or the UI, without changing the test.

To achieve this, first define in `conftest.py` a parameterized PyTest fixture like this:

```python
import pytest
from verifit.driver import get_driver_params, get_driver_name
@pytest.fixture(params=get_driver_params('SHOPPING_DRIVER')(['shopping-service']))  # (1)
def shopping_driver(request):
    return get_driver_name(request)  # (2)
```

Then, in your test, say:

```python
import pytest
from verifit.driver import get_driver
from verifit.login import login_from_cache
def test_products(shopping_driver_name):  # (3)
    get_user = get_driver(shopping_driver_name)('user')  # (4)
    user = get_user('MAIN')  # (5)
    do_login = get_driver(shopping_driver_name)('login')  # (6)
    login_from_cache(user)(do_login)  # (7)
    # ... actual test, we're now logged in
```

Explanation:

- At (1) we define a PyTest fixture that takes the params as returned by the `get_driver_params` library function from `verifit`.  This function returns either:
   - A list obtained by splitting at comma (`,`) the value of the environment variable whose name is given in the first parameter (`'SHOPPING_DRIVER'` in this case).
   - The list defined by the second parameter (`['shopping-service']`) in case that the environment variable is not defined.
   - In our case, it will return, e.g., `'shopping-service'`.
- At (2), the fixture just calls `get_driver_name(request)`.  Here `request` is the standard PyTest way of giving the fixture access to the calling context.  What `get_driver_name` does, is:
   - Mark the requesting test as skipped if `skip_drivers` is present, see [above conftest section](#2-prepare-a-conftestpy-file-with-driver-names) for an example.
   - Return `request.param`, which is essentially the parameter value obtained from the params list added to the fixture, e.g., `'shopping-service'`.
- At (3) we let PyTest know that this test needs the `shopping_driver_name` fixture we defined at (1).
- At (4), we get the user driver, by calling `get_user = get_driver(shopping_driver_name)('user')`.  This will:
   - Compose the name `<shopping_driver_name>_user`.  In this case, the composed name will be `'shopping-service_user'`.
   - Load a Python module by that name, from the same directory as the test file.
   - Return that module's `execute()` function.
   - Note that the `execute()` function is not being called here, but returned as a first-class object.
   - In our case, the driver will return the `execute(user_type)` function that's defined in `shopping-service_user.py`.
- At (5), we call that driver with `'MAIN'`, which effectively returns the main user for that driver.
- At (6), we ge the login driver, which we call `do_login`.  This works the same as for `user`.
- At (7) we call `login_from_cache(user)(do_login)`, which will call `do_login(user)` and extract the login data from the result.


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

- Go to `tests/kitchen-service/ui` and run `yarn install`.
- Install sample tests requirements. Run:

   ```shell
   cd tests/ && pip install -r requirements.txt
   ```
Change tests code, then make sure to test, document, & push your changes.
