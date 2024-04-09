import jwt
import pytest
from datetime import datetime, timedelta
from src import login, login_from_cache, cache_set, cache_get, LoginData


# Fixture for a mock authentication driver
@pytest.fixture
def mock_driver():
	def driver(username: str, secret: str) -> str:
		# Simulates generating an encoded token just enough time left in order to pass the test
		expiry_date = datetime.now() + timedelta(minutes=6)

		def _encode_jwt():
			payload = {
				"sub": username,
				"exp": expiry_date.isoformat()
			}
			encoded_jwt = jwt.encode(payload, secret, algorithm="HS256")
			return encoded_jwt

		return _encode_jwt()

	return driver


# Fixture for user credentials
@pytest.fixture
def user_credentials():
	return "test-user", "test-secret"


# Fixture for clearing user cache before each test
@pytest.fixture(autouse=True)
def clear_user_cache(user_credentials):
	username, _ = user_credentials
	cache_set(username)(None)


def test_login_success(mock_driver, user_credentials):
	username, secret = user_credentials
	login_data = login(driver=mock_driver, username=username, secret=secret)
	assert isinstance(login_data, LoginData)
	assert jwt.decode(login_data.access_token, algorithms=["RS256", "HS256"], options={"verify_signature": False})
	assert login_data.expiry_date > datetime.now()


def test_login_from_cache_with_fresh_data(mock_driver, user_credentials):
	username, secret = user_credentials
	# First, perform a login to ensure data is cached
	initial_login_data = login(driver=mock_driver, username=username, secret=secret)

	# Then, attempt to log in from cache
	cached_login_data = login_from_cache(driver=mock_driver, username=username, secret=secret)
	assert isinstance(cached_login_data, LoginData)
	assert cached_login_data.access_token == initial_login_data.access_token
	assert cached_login_data.expiry_date == initial_login_data.expiry_date


def test_login_from_cache_with_almost_expired_data(mock_driver, user_credentials):
	username, secret = user_credentials
	# Manually cache data with an expiry date 4 minutes from now
	almost_expired_login_data = LoginData(
		access_token="almost_expired_token",
		expiry_date=datetime.now() + timedelta(minutes=4)
	)
	cache_set(username)(almost_expired_login_data.to_dict())

	# Attempt to log in from cache, expecting it to perform a new login
	new_login_data = login_from_cache(driver=mock_driver, username=username, secret=secret)
	assert isinstance(new_login_data, LoginData)
	assert new_login_data.access_token != almost_expired_login_data.access_token
	assert new_login_data.expiry_date > datetime.now()
