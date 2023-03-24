from datetime import datetime

from requests.auth import AuthBase

from .driver import get_driver

from .cache import cache_set, cache_get
from .config import get_store_reader, get_store_writer
from .date_and_time import date_diff_in_minutes
from .iam_token import decode_token, get_token_expiration_date

get_env = get_store_reader()
set_env = get_store_writer()

ACCESS_TOKEN = 'accessToken'
EXPIRY_DATE = 'expiryDate'
LOGIN_DATA = 'loginData'
USERNAME = 'username'
PASSWORD = 'password'


def get_expiry_date(login_data):
    return datetime.fromisoformat(login_data.get(EXPIRY_DATE, None))


def get_login_user_name(user):
    return user.get(USERNAME, None)


def get_login_user_password(user):
    return user.get(PASSWORD, None)


def login(user):
    def with_driver(driver):
        access_token = driver(user)
        decoded_token = decode_token(access_token)
        token_expiry_date = get_token_expiration_date(decoded_token)
        login_data = {
            ACCESS_TOKEN: access_token,
            EXPIRY_DATE: token_expiry_date.isoformat()
        }
        cache_set(get_login_user_name(user))(login_data)
        set_env(LOGIN_DATA)(login_data)
        return login_data
    return with_driver


def login_main_user(driver_name):
    user = get_driver(driver_name)('user')('MAIN')
    return login(user)(get_driver(driver_name)('login'))


def login_main_user_from_cache(driver_name):
    user = get_driver(driver_name)('user')('MAIN')
    return login_from_cache(user)(get_driver(driver_name)('login'))


def get_login_values_from_cache(username):
    user_cached_data = cache_get(username)
    if user_cached_data is None:
        print(f"Cache miss key <{username}>, no cached data")
        return None
    token_expiry_iso_string = user_cached_data.get('expiryDate', None)
    if token_expiry_iso_string is None:
        print(f"Cache miss key <{username}>, no expiration info")
        return None
    token_expiry_date = datetime.fromisoformat(token_expiry_iso_string)
    minutes = date_diff_in_minutes(token_expiry_date)(datetime.now())
    if minutes < 10:
        print(f"Cache miss key <{username}>, almost expired")
        return None
    print(f"Cache hit key <{username}>")
    login_data = {
        ACCESS_TOKEN: user_cached_data.get(ACCESS_TOKEN, None),
        EXPIRY_DATE: token_expiry_date
    }


def login_from_cache(user):
    def with_driver(driver):
        login_data = get_login_values_from_cache(get_login_user_name(user))
        if login_data is None:
            login_data = login(user)(driver)
        print(f"Caching login data <{login_data}>")
        set_env(LOGIN_DATA)(login_data)
        return login_data
    return with_driver


def get_bearer_authorization_header_value():
    login_data = get_env(LOGIN_DATA)
    print(f"Using cached login data <{login_data}>")
    return f"Bearer {login_data.get(ACCESS_TOKEN, None)}"


def get_bearer_auth_base():
    class BearerAuth(AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r

    return BearerAuth(get_access_token_from_env())
