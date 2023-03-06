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

Normally, if you're using PyTest and a few helper Python modules, you can test pretty much anything quite fast, without needing a library.  However, as you start doing this, you soon realize you're going to need some things over and over again in your tests.  This small library provides a few helpers for making a developer's automatic testing easier:

- Quick configuration.
- A cache for speeding up things such as getting access tokens, or any other data that is reused.
- A quick way to do driver-based testing, in which the test case relies on a particular driver (specified at runtime)  that does the action and returns the result.  This allows you to run the same test against different drivers, such as an API, UI, etc.
- Simplified mechanism for skipping tests that are not suitable for a particular driver.
- Web-Sockets testing.
- Some other helper tools, like date & time, generating random values.

This repo consists of the actual library, which is in `lib/`, some sample shell scripts, and sample tests from which you can inspire.


# Quick Start with Writing Tests

## 1. Install Required Libraries

- Install Python 3.6 or higher.
- Install PyTest.
- Copy the [requirements from the sample tests](https://github.com/sorelmitra/verifit/blob/main/tests/requirements.txt) to your PyTest project and install them.  This will basically install the `verifit` library to its latest version.

## 2. Prepare a `conftest.py` File with Drivers

**Note 1**: You can skip this section if you're not going to use drivers in your tests.

**Note 2**: You can see the pattern explained below applied for the sample tests in  `tests/conftest.py`.

Assume you have two services, `my-service`, and `my-second-service`, and each one of them has different needs for a driver:

- `my-service` has a REST, GraphQL, and UI interface, and you want to test them all, ideally without duplicating test cases.  The use cases for all interfaces are similar and you want to reuse your test cases.
- `my-second-service` has multiple versions, and most of your tests apply to all of them, so again  you want to reuse them.

To achieve this with this library, add the following code into your `conftest.py` file:

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

(In the rest of this section, we focus on `my-service`.  The same pattern applies for `my-second-service`.)

Then in your test file, use the driver like this:

```python
@pytest.mark.driver_functionality('do_stuff')
def test_stuff(my_driver):
   data = {}  # the data that <do_stuff> needs
   my_driver(data)
```

Now the framework will make sure to call `do_stuff` for each driver that is specified in the environment variable `MY_DRIVER`, or by default for the list declared in the fixture: `['my-service-rest', 'my-service-graphql', 'my-service-ui']`.  Specifically, it will look for files named like this, in the same folder as your test file:

- `my-service-rest-do_stuff.py`: Do stuff via REST.
- `my-service-graphql-do_stuff.py`: Do stuff via GraphQL.
- `my-service-ui-do_stuff.py`: Do stuff via UI.

If you need to specify `MY_DRIVER`, do it like this: `MY_DRIVER='my-service-rest,my-service-ui' pytest my-tests`.  This will run your tests for only the REST and UI drivers.

In case a particular test does not make sense for a particular driver, mark it as such with:

```python
@pytest.mark.skip_driver('my-service-ui')
@pytest.mark.driver_functionality('do_another_stuff')
def test_another_stuff(my_driver):
   data = {}  # the data that <do_another_stuff> needs
   my_driver(data)
```

Now the framework will skip `test_another_stuff` if the driver is for UI, and instruct PyTest to display an appropriate message.

## 3. Inspire from the Sample Tests 

We have a bunch of test suites that you can inspire from.  Each suite tests an imaginary service, which is either an online dummy one, either a dummy shell command. 

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

To run all sample test suites included with this project, do this:

```shell
cd tests
pip install -r requirements.txt
pytest .
```

More example commands:

- Run only tests that are related to posts and shopping: `pytest post-service shopping-service`.
- Run the posts tests only with the first driver: `POST_DRIVER='post-service-1' pytest post-service`.
- Run the posts tests with all drivers explicitly: `POST_DRIVER='post-service-1,post-service-2' pytest post-service`.
   - **Note**: In our case, this is the same as not specifying `POST_DRIVER` at all.  _However_, this is a useful pattern in case you have N>2 drivers and want to run just a few of them.

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




# Development

## Library

If you want to develop, build, and upload this library to PyPI, do this:

First, set up a few things:

- Install Python 3.6 or higher.
- Install the requirements from `requirements.txt`.

The lib code is in `src/verifit`.  Make sure to use proper `.` imports to avoid importing from the installed `verifit` library accidentally.

Once your code changes are ready and documented (if need be), do the following to upload:

1. Commit everything to GIT.

2. Check Manifest: Run `check-manifest`.

3. Increase the version in `pyproject.toml`:

   ```toml
   [project]
   version = "1.0.6"
   ```

4. Increase the minimum version in `tests/requirements.txt`:

   ```
   verifit >= 1.0.6
   ```

5. Build package. Run:

   ```shell
   python -m build
   ```

6. Check build. Run:

   ```shell
   twine check dist/verifit-1.0.6*
   ```

7. Upload to Test.PyPI. Run:

   ```shell
   twine upload -r testpypi dist/verifit-1.0.6*
   ```

8. Install manually from Test.PyPI. Run:

   ```shell
   pip install -i https://test.pypi.org/simple verifit==1.0.6
   ```

   (First time it may fail, in this case, rerun the above command.)

9. Run the sample tests:

   ```shell
   cd tests/ && pytest .
   ```

10. If everything goes well, upload to PyPI. Run:

   ```shell
   twine upload dist/verifit-1.0.6*
   ```

11. Install sample tests requirements. Run:

   ```shell
   cd tests/ && pip install -r requirements.txt
   ```

12. Run the sample tests again:

   ```shell
   cd tests/ && pytest .
   ```

If all went well, they should pass.  You can now push to GIT.

## Sample Tests

Setup:

- Go to `tests/kitchen-service/ui` and run `yarn install`.
- Install sample tests requirements. Run:

   ```shell
   cd tests/ && pip install -r requirements.txt
   ```
Change tests code, then make sure to test, document, & push your changes.
