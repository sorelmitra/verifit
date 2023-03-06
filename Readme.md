# About

This is a Python library that simplifies setting up and using automatic system testing for several types of projects.

I've named it `verifit` as a contraction of `Verify It!`, i.e. "Make sure your system works fine!"



# Introduction

System testing (or application-level testing) is a must for every project.  Even if you have a dedicated QA team, automatic system testing is a very valuable tool for making sure your product works as expected.

Usually you can't test a system 100% automatically. But, if you manage to cover the functionality (and perhaps some non-functional requirements, such as performance and high-availability - depending on the nature of the project), this will be a big help as the project builds up, and the risk of breaking something increases.

Also, on small projects or where you're time constrained, having an automatic system testing framework that's easy to put to use on a daily basis is of great help.

There are multiple ways of writing automated tests.  One particular way I favor is **black box testing**, in which you treat your system as a black box, and *never check its internals*.  I find it has quite a few advantages:

- Easy to put in place.  You just hit your system in the same way its clients would.  No need to write code that checks databases, Kafka, or who knows what.
- Can serve as acceptance testing.  You can put up compound scenarios.
- It's resistant to system implementation changes.

While I do favor black-box testing, this library is suitable for any type of testing you wish.



# Overview

Normally, if you're using PyTest and a few helper Python modules, you can test pretty much anything quite fast, without needing a library.  However, as you start doing this, you soon realize you're going to need some things over and over again in your tests.  This small library provides a few helpers for making a developer's automatic testing easier:

- Quick configuration.
- A cache for speeding up things such as getting access tokens, or any other data that is reused.
- A quick way to do driver-based testing, in which the test case relies on a particular driver (specified at runtime)  that does the action and returns the result.  This allows you to run the same test against different drivers, such as an API, UI, etc.
- Simplified mechanism for skipping tests that are not suitable for a particular driver.
- Web-Sockets testing.
- Some other helper tools, like date & time, generating random values.

This repo consists of the actual library, which is in `lib/`, some sample shell scripts, and sample tests from which you can inspire.


# Quick Start

## 1. Install Required Libraries

- Install Python 3.6 or higher.
- Add library to `PYTHONPATH`: `export PYTHONPATH=<verifit repo>/lib:$PYTHONPATH`.
- Install the requirements from `requirements.txt`.
- Go to `tests/kitchen-service/ui` and run `yarn install`.

## 2. Prepare a `conftest.py` File with Drivers

**Note 1**: You can skip this section if you're not going to use drivers in your test.

**Note 2**: You can see the pattern explained below applied in the `./conftest.py`, for the sample tests.

For each driver type you're going to need, add the following code into your `conftest.py` file:

```python
import pytest

from src.lib.driver import get_driver_params, get_driver


@pytest.fixture(params=get_driver_params('MY_DRIVER', ['my-service-rest', 'my-service-graphql', 'my-service-ui']))
def my_driver(request):
    return get_driver(request)


@pytest.fixture(params=get_driver_params('MY_SECOND_DRIVER', ['my-second-service-v1', 'my-second-service-v2', 'my-second-service-v3', 'my-second-service-v4']))
def my_second_driver(request):
    return get_driver(request)
```

Then in your test file, use the driver like this:

```python
@pytest.mark.driver_functionality('do_stuff')
def test_stuff(my_driver):
   data = {}  # the data that <do_stuff> needs
   my_driver(data)
```

(Similarly for the `my_second_driver` driver.)

Now the framework will make sure to call `do_stuff` for each driver that is specified in the environment variable `MY_DRIVER`, or for all of them declared in the fixture.  Specifically, it will look for files named like this, in the same folder as your test file:

- `my-service-rest-do_stuff.py`: Do stuff via REST.
- `my-service-graphql-do_stuff.py`: Do stuff via GraphQL.
- `my-service-ui-do_stuff.py`: Do stuff via UI.

In case a particular test does not make sense for a particular driver, mark it as such with:

```python
@pytest.mark.skip_driver('my-service-ui')
@pytest.mark.driver_functionality('do_another_stuff')
def test_another_stuff(my_driver):
   data = {}  # the data that <do_another_stuff> needs
   my_driver(data)
```

Thus, `test_another_stuff` will be skipped for driver `my-driver-ui`.

## 3. Inspire from the Sample Tests 

We have a bunch of suites that you can inspire from.  Each suite tests an imaginary service, which is either an online dummy one, either a dummy shell command. 

1. **Post-Service**.  This one can post to a particular server via a driver.  Each driver connects to the server it can talk to, and makes sure the returned data has the same format in order for the test to function.  We have the following drivers:
   - `post-service-1` that connects to a REST API.
   - `post-service-2` that connects to a GraphQL API.
2. **Echo-Service**.  It sends a message to a Web-Sockets server and gives back the response.  In our case, the dummy WSS server echoes back whatever we're sending, so the test verifies this.
3. **Shopping-Service**.  This test shows multiple features:
   - Login and get an access token.  (`test_login.py`.)
   - Accessing an authorized endpoint with an access token.  (`test_products.py`.)
   - Caching some values, in this case the access token for a particular user.  (`test_login.py`.)
   - Log in from cache, which means reusing the cached access token if it's not close to expiration date.  If no suitable token is found, log in again.  (`test_products.py`.)
   - BDD using `pytest-bdd` and Gherkin.  Implements a similar test to `test_products.py`, but this time with a Gherkin feature file and `@given`, `@when`, `@then`.  Showcases matching a Gherkin declaration with regular expressions.  (`test_carts.py`.)
4. **Date-Service**.  It runs the shell command `date` with some arguments, and verifies the resulting output.
5. **Kitchen-Service**.  Web UI test using Cypress.IO and their kitchen sink sample page.  It is called from a Python test that runs Cypress via `subprocess`.

## 4. Write Some Tests

You can now start writing tests!  (Perhaps by copying one of the samples.)

## Run Tests

Run your tests as usual, by invoking `pytest`.

To run the sample tests included with this project, here're some example commands:

- Run `pytest tests/` to run all tests.
- Run only tests that are related to posts and shopping: `pytest tests/post-service tests/shopping-service`.
- Run the posts tests only with the first driver: `POST_DRIVER='post-service-1' pytest -vv tests/post-service`.
- Run the posts tests with all drivers explicitly: `POST_DRIVER='post-service-1,post-service-2' pytest -vv tests/post-service`.
   - **Note**: In our case, this is the same as not specifying `POST_DRIVER` at all.  _However_, this is a useful pattern in case you have N>2 drivers and want to run just a few of them.


# Reference

The entire library is coded using Functional Programming principles.  Thus, you will see:

- At most one argument for each function.
- Higher-order functions - that return another function.
- The memoize pattern used to make sure a single instance of a thing exists (in our case the config store).

Helpers:

- `cache.py`.  Implements a simple cache, stored in `.<env>-cache.json` 
- `config.py`.  Loads configuration via `dotenv` package, and returns a memoized store for getting/setting values.
- `date_and_time.py`.  Some simple date/time utils, such as a diff.
- `driver.py`.  Imports a driver based on a driver name.  Built for calling from `conftest.py`, see above section for [preparing drivers](#2-prepare-a-conftestpy-file-with-drivers).
- `generate.py`.  Functions to generate some data.
- `iam_token.py`.  Decoding and extracting data from a JWT.
- `login.py`.  Functions to log in or log in from cache, and for building authorization values (one for REST, one for the Python GraphQL client.)
- `memoize.py`.  Simple memoize pattern.
- `web_sockets.py`.  Simplifies Web-Sockets testing by listening in background for received packages, and sending data.
