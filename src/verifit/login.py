from datetime import datetime

from requests.auth import AuthBase

from .cache import cache_set, cache_get
from .config import get_store_reader, get_store_writer
from .date_and_time import date_diff_in_minutes
from .iam_token import decode_token, get_token_expiration_date

get_env = get_store_reader()
set_env = get_store_writer()

KEY_ACCESS_TOKEN = 'access_token'
KEY_EXPIRY_DATE = 'expiry_date'
KEY_LOGIN_DATA = 'login_data'
KEY_USERNAME = 'username'
KEY_PASSWORD = 'password'


def get_access_token(login_data):
    return login_data.get(KEY_ACCESS_TOKEN, None)


def get_access_token_from_env():
    return get_access_token(get_env(KEY_LOGIN_DATA))


def get_expiry_date(login_data):
    return login_data.get(KEY_EXPIRY_DATE, None)


def get_expiry_date_from_env():
    return get_expiry_date(get_env(KEY_LOGIN_DATA))


def create_login_data():
    login_data = {}

    def with_access_token(access_token):
        login_data[KEY_ACCESS_TOKEN] = access_token

        def with_expiry_date(expiry_date):
            login_data[KEY_EXPIRY_DATE] = expiry_date
            return login_data

        return with_expiry_date

    return with_access_token


def get_login_user_name(user):
    return user.get(KEY_USERNAME, None)


def get_login_user_password(user):
    return user.get(KEY_PASSWORD, None)


def create_login_user():
    login_user = {}

    def with_username(username):
        login_user[KEY_USERNAME] = username

        def with_password(password):
            login_user[KEY_PASSWORD] = password
            return login_user

        return with_password

    return with_username


def login(user):
    def with_driver(login_driver):
        access_token = login_driver(user)
        decoded_token = decode_token(access_token)
        token_expiry_date = get_token_expiration_date(decoded_token)
        cache_set(get_login_user_name(user), {
            'accessToken': access_token,
            'expiryDate': token_expiry_date.isoformat()
        })
        login_data = create_login_data()(access_token)(token_expiry_date)
        set_env(KEY_LOGIN_DATA)(login_data)
        return login_data
    return with_driver


def get_login_values_from_cache(username):
    user_cached_data = cache_get(username)
    if user_cached_data is None:
        return None
    token_expiry_iso_string = user_cached_data.get('expiryDate', None)
    if token_expiry_iso_string is None:
        return None
    token_expiry_date = datetime.fromisoformat(token_expiry_iso_string)
    minutes = date_diff_in_minutes(token_expiry_date, datetime.now())
    if minutes < 10:
        return None
    return create_login_data()(user_cached_data.get('accessToken', None))(token_expiry_date)


def login_from_cache(user):
    def with_driver(login_driver):
        login_data = get_login_values_from_cache(get_login_user_name(user))
        if login_data is None:
            login_data = login(user)(login_driver)
        set_env(KEY_LOGIN_DATA)(login_data)
        return login_data
    return with_driver


def get_bearer_authorization_header_value():
    return f"Bearer {get_access_token_from_env()}"


def get_bearer_auth_base():
    class BearerAuth(AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r

    return BearerAuth(get_access_token_from_env())
