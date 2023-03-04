# About

This is a Python library that simplifies setting up and using automatic system testing for several types of projects.

I've named it `verifit` as a contraction of `Verify It!`, i.e. "Make sure your system works fine!"



# Introduction

System testing (or application-level testing) is a must for every project.  Even if you have a dedicated QA team, automatic system testing is a very valuable tool for making sure your product works as expected.

Usually you can't test a system 100% automatically. But, if you manage to cover the functionality (and perhaps some non-functional requirements, such as performance and high-availability - depending on the nature of the project), this will be a big help as the project builds up, and the risk of breaking something increases.

Also, on small projects or where you're time constrained, having an automatic system testing framework that's easy to put to use on a daily basis is of great help.



# Overview

Normally, if you're using PyTest and a few helper Python modules, you can test pretty much anything quite fast, without needing a library.  However, as you start doing this, you soon realize you're going to need some things over and over again in your tests.  This small library provides a few helpers for making a developer's automatic testing easier:

- Quick configuration.
- A cache for speeding up things such as getting access tokens, or any other data that is reused.
- A quick way to do driver-based testing, in which the test case relies on a particular driver (specified at runtime)  that does the action and returns the result.
- Web-Sockets testing.
- Some other helper tools, like date & time, generating random values.
- Some POSIX shell scripts for running driver-based test suites, and for grouping together tests that are ran in different manners.

This repo consists of the actual library, which is in `lib/`, some sample shell scripts, and sample tests from which you can inspire.


# Quick Start

## Setup

- Install Python 3.6 or higher.
- Add library to `PYTHONPATH`: `export PYTHONPATH=<verifit repo>/lib:$PYTHONPATH`.
- Install the requirements from `requirements.txt`.
- Go to `kitchen-service/ui` and run `yarn install`.

## Inspect the Sample Tests 

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

## Start Testing

You can now start writing tests!  (Perhaps by copying one of the samples.)



# Reference

## Python Helpers

The entire library is coded using Functional Programming principles.  Thus, you will see:

- At most one argument for each function.
- Higher-order functions - that return another function.
- The memoize pattern used to make sure a single instance of a thing exists (in our case the config store).

Helpers:

- `cache.py`.  Implements a simple cache, stored in `.<env>-cache.json` 
- `config.py`.  Loads configuration via `dotenv` package, and returns a memoized store for getting/setting values.
- `date_and_time.py`.  Some simple date/time utils, such as a diff.
- `driver.py`.  Imports a driver based on a driver name and folder and a functionality name.
- `generate.py`.  Functions to generate some data.
- `iam_token.py`.  Decoding and extracting data from a JWT.
- `login.py`.  Functions to log in or log in from cache, and for building authorization values (one for REST, one for the Python GraphQL client.)
- `memoize.py`.  Simple memoize pattern.
- `web_sockets.py`.  Simplifies Web-Sockets testing by listening in background for received packages, and sending data.

## Shell Scripts

1. `run-tests.sh` runs all sample test groups.  One group is the Post-Service tests, which use drivers for testing, and are executed via a dedicated script that can start them for each configured driver.  The other one is all other tests, which are executed with PyTest directly.
2. `run-post-service-tests.sh` runs the Post-Service tests, once for each of the two drivers.
3. `lib.sh` contains helper library functions for the above scripts.
4. `run-post-service-*.sh` run the appropriate driver for Post-Service tests.
