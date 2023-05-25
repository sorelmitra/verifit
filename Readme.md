# About

This is a Python library aimed at developers, that simplifies setting up and using automatic system testing for several types of projects.

I've named it `verifit` as a contraction of `Verify It!`, i.e. "Make sure your system works fine!"



# Introduction

## Why Developer-Based Automatic System Testing?

Automatic system (or application-level) testing done by developers is a must for every project.  Even if you have a dedicated QA team, automatic system testing is a very valuable tool for making sure your product works as expected:

- It allows developers to be very confident of the quality of the products that they ship.
- It lowers the risk of breaking older functionality as you add a new one.
- It makes bug investigation easier - if you know that the behavior shown in the bug passes in your automated tests, then the source must be elsewhere, such as misconfiguration or wrong parameter.
- It makes QA team's life easier by helping them design their tests.

## Why This Libray?

For the above to work, though, the developers must be maintaining their tests along with the code base, or even better, do TDD.

This library aims to make a developer's life easier by providing a handful of commonly used options, such as environment variables or making authorized HTTPS requests.  The goal is to get started with automated tests right away!

## Side Note: Black Box Testing

There are multiple ways of writing automated tests, and this library is not tied to any particular methodology.

However, one particular testing methodology I favor is **black box testing**, in which you treat your system as a black box, and *never check its internals*.  I find it has quite a few advantages, and I thought I'd list some of them here:

- Easy to put in place.  You just hit your system in the same way its clients would.  No need to write code that checks databases, message queues, or who knows what.
- Can serve as acceptance or end-to-end testing.
- It's not affected by implementation changes in the system that's being tested.




# Overview

This library supports any type of tests that you write in Python, using any testing framework.

For our sample tests, we use the PyTest runner & framework.

Normally, if you're using PyTest and a few other standard Python modules, you can test pretty much anything quite fast, without needing a library.  However, as you start doing this, you soon realize you're going to need some things over and over again in your tests.  This small library provides a few helpers for making a developer's automatic testing easier:

- Quick configuration & data sharing between tests.
- A cache for speeding up things such as getting access tokens, or any other data that is being reused.
- Log in and caching the access token.
- Some helper tools, like date, JWT, accessing dictionary properties, etc.
- Web-Sockets testing.  (I couldn't find a Python package that makes testing Web-Sockets as easy as calling a couple of functions.)

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
- `.dev.env`: Hosts configuration for our tests, such as endpoints or users.
- `__init__.py`: Needed for local imports.
- `conftest.py`: Needed for local imports.

### 2.2. Sample Tests

The sample tests use dummy online services or commands in order to show how to test various types of applications, and how to use our lib: 

1. `post_service/post/test_post.py`. Tests simple APIs using HTTP and GraphQL servers.

2. `post_service/drivers/test_post_via_drivers.py`. The same as `test_post.py`, but showcasing using different drivers.

   If you need to run your tests through multiple channels, then it's best if you keep your tests unified, and add a couple of layers to help directing the tests through the right channel.

    Assume you need to 'Post' items via two channels, 'foo', and 'bar'.  The layers would be:
    
    1. Test declaration
    	- Does the actual testing, 'Posting' an item and verifying the result
    	- Does not call directly to 'foo' or 'bar'
    	- Calls to a Domain-Specific Language, aka DSL
    2. DSL implementation
    	- Based on the 'driver' parameter, it calls either to 'foo' or 'bar'
    3. Drivers implementation
    	- Each driver 'Posts' items in the way it knows
    	- There is one driver implementation for each channel, i.e., 'foo' and 'bar'
        - If 'bar' cannot 'Post' an item, then the corresponding driver is missing 

    The files:

    - `drivers.py` contains the list of our particular drivers
    - The test itself is straightforward, as it imports the DSL, calls it, and verifies the result.  Note that the test is skipped for the 'bar' driver, because in our example, we are pretending that the 'bar' channel has no way to 'Post an item.
    - `dsl_post.py`: The DSL uses the driver lib to call to the right driver from a driver map it provides.  In our case, the 'foo' driver is omitted from the map, because we know it cannot create an 'Item'.
    - `driver_foo.py`: The 'foo' driver to 'Post' an item.  The 'bar' driver to 'Post' an item does not exist, as it cannot perform this action.

    To run this test via the 'bar' driver, do this:

    ```
    DRIVER=bar pytest . -k 'post'
    ```
   
    By default, `DRIVER` is `foo`.

3. `shopping_service/login/test_login.py`. Here we test log in to a server.

4. `shopping_service/login/test_products.py`. This one does the following:

   - Log in from cache.  This returns the cached token if it is valid, or logs in and caches the token before returning it.
   - Call to a private endpoint, passing in an authorization header with a cached access token.

5. `shopping_service/login/test_carts.py`. It shows Gherkin features and BDD.

6. `echo_service/test_echo_service.py`.  Shows how to simplify testing WebSockets using our library.

    **Note**: As of _2023-04-26_, the online server that we were using for this sample test stopped accepting the API key that they provide.  As a result, we've marked this test as skipped.

7. `date_service/test_date.py`.  Shows how to test CLI programs using this lib: it runs the shell command `date` with some arguments, and verifies the resulting output.

8. `self_check/test_self.py`.  Tests the lib itself.

9. `kitchen_service/test_kitchen_service.py`.  Showcase doing a Web UI test using Cypress.IO and their kitchen sink sample page.

To prepare for running the sample tests that are included with this project, do this:

```shell
cd tests
pip install -r requirements.txt
```

To run all tests:

```shell
pytest .
```

To run only tests that are related to posts and shopping:

```shell
pytest . -k 'post_service or shopping_service'
```

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

- `cache.py`.  Implements a simple cache, that is being stored in a file named `.<env>-cache.json` from the `tests` directory.
- `config.py`.  Loads configuration via the `dotenv` package, and returns a unique store for getting/setting values across tests.
- `date_diff.py`.  Simple date diff.
- `driver.py`.  The driver lib is pretty simple:
    - It gets the current driver from the environment
    - It calls the corresponding function from a driver name / function dict
    - It also offers a helper function to skip a test for a particular driver
- `json_web_token.py`.  Decoding and extracting data from a JWT.
- `login.py`.  Functions to:
    - Log in using a driver, which is a plain function.  We use a driver for this because logging in is particular to the API that each project has.  The driver does the actual call to the API endpoint for login, and returns the access token.  The framework caches the access token and its expiration date.
    - Log in from a cached token using a driver.
    - Building authorization values:
      - For HTTP headers.
      - For the Python GraphQL client.
- `memoize.py`.  Simple memoize pattern, used by `config.py` to provide a single store instance for sharing data across tests.
- `prop.py`: Access dictionary properties without raising exceptions, and with default values.
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
