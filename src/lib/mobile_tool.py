import copy
import datetime
import inspect
import json
import os
import re
import subprocess
from shutil import copyfile

import pytest
from appium import webdriver
from selenium.common.exceptions import InvalidSessionIdException

from relative_path import RelativePath


ANDROID_BASE_CAPS = {
    'automationName': 'UIAutomator2',
    'platformName': 'Android',
    'platformVersion': os.getenv('ANDROID_PLATFORM_VERSION') or '10',
    'deviceName': os.getenv('ANDROID_DEVICE_VERSION') or 'Android Emulator',
}

IOS_BASE_CAPS = {
    'automationName': 'xcuitest',
    'platformName': 'iOS',
    'platformVersion': os.getenv('IOS_PLATFORM_VERSION') or '13.3',
    'deviceName': os.getenv('IOS_DEVICE_NAME') or 'iPhone 8',
    # 'showIOSLog': False,
}

EXECUTOR = 'http://127.0.0.1:4723/wd/hub'


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def take_screenshot_and_logcat(driver, device_logger, calling_request):
    __save_log_type(driver, device_logger, calling_request, 'logcat')


def take_screenshot_and_syslog(driver, device_logger, calling_request):
    __save_log_type(driver, device_logger, calling_request, 'syslog')


def __save_log_type(driver, device_logger, calling_request, log_type):
    logcat_dir = device_logger.logcat_dir
    screenshot_dir = device_logger.screenshot_dir

    try:
        driver.save_screenshot(os.path.join(screenshot_dir, calling_request + '.png'))
        logcat_data = driver.get_log(log_type)
    except InvalidSessionIdException:
        logcat_data = ''

    with open(os.path.join(logcat_dir, '{}_{}.log'.format(calling_request, log_type)), 'w') as logcat_file:
        for data in logcat_data:
            data_string = '%s:  %s\n' % (data['timestamp'], data['message'].encode('utf-8'))
            logcat_file.write(data_string)


def configure_logging_and_screenshots(config):
    if not hasattr(config, 'input'):
        base_path = RelativePath().script_path('')
        current_day = '{:%Y-%m-%d-%H%M}'.format(datetime.datetime.now())
        ensure_dir(os.path.join(base_path, 'input', current_day))
        result_dir = os.path.join(base_path, 'results', current_day)
        ensure_dir(result_dir)
        result_dir_test_run = result_dir
        ensure_dir(os.path.join(result_dir_test_run, 'screenshots'))
        ensure_dir(os.path.join(result_dir_test_run, 'logcat'))
        config.screen_shot_dir = os.path.join(result_dir_test_run, 'screenshots')
        config.logcat_dir = os.path.join(result_dir_test_run, 'logcat')


class DeviceLogger:
    def __init__(self, logcat_dir, screenshot_dir):
        self.screenshot_dir = screenshot_dir
        self.logcat_dir = logcat_dir


@pytest.fixture(scope='function')
def device_logger(request):
    logcat_dir = request.config.logcat_dir
    screenshot_dir = request.config.screen_shot_dir
    return DeviceLogger(logcat_dir, screenshot_dir)


@pytest.fixture(scope='function')
def driver_android(request, device_logger):
    calling_request = request._pyfuncitem.name

    caps = copy.copy(ANDROID_BASE_CAPS)
    caps['name'] = calling_request
    caps['app'] = request.config.ANDROID_APP
    caps['appActivity'] = request.config.ANDROID_APP_ACTIVITY

    driver = webdriver.Remote(
        command_executor=EXECUTOR,
        desired_capabilities=caps
    )

    def fin():
        take_screenshot_and_logcat(driver, device_logger, calling_request)
        driver.quit()

    request.addfinalizer(fin)

    driver.implicitly_wait(10)
    return driver


@pytest.fixture(scope='function')
def driver_ios(request, device_logger):
    calling_request = request._pyfuncitem.name

    caps = copy.copy(IOS_BASE_CAPS)
    caps['name'] = calling_request
    caps['app'] = request.config.IOS_APP

    driver = webdriver.Remote(
        command_executor=EXECUTOR,
        desired_capabilities=caps
    )

    def fin():
        take_screenshot_and_syslog(driver, device_logger, calling_request)
        driver.quit()

    request.addfinalizer(fin)

    driver.implicitly_wait(10)
    return driver
