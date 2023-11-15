from datetime import datetime

from .cache import cache_set, cache_get
from .config import get_env_reader
from .date_tools import date_subtract_in_minutes
from .json_web_token import decode_token, get_token_expiration_date

get_env = get_env_reader()

ACCESS_TOKEN = 'accessToken'
EXPIRY_DATE = 'expiryDate'


def get_expiry_date(login_data):
    return datetime.fromisoformat(login_data.get(EXPIRY_DATE))


def login(driver=None, username=None, password=None):
    access_token = driver(username=username, password=password)
    decoded_token = decode_token(access_token)
    token_expiry_date = get_token_expiration_date(decoded_token)
    login_data = {
        ACCESS_TOKEN: access_token,
        EXPIRY_DATE: token_expiry_date.isoformat()
    }
    cache_set(username)(login_data)
    return login_data


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
    minutes = date_subtract_in_minutes(from_date=token_expiry_date, date_to_subtract=datetime.now())
    if minutes < 10:
        print(f"Cache miss key <{username}>, almost expired")
        return None
    print(f"Cache hit key <{username}>")
    login_data = {
        ACCESS_TOKEN: user_cached_data.get(ACCESS_TOKEN),
        EXPIRY_DATE: token_expiry_date
    }
    return login_data


def login_from_cache(driver=None, username=None, password=None):
    login_data = get_login_values_from_cache(username)
    if login_data is None:
        login_data = login(driver=driver, username=username, password=password)
    print(f"Caching login data <{login_data}>")
    return login_data

