import pytest
import requests
from pytest_bdd import given, parsers, scenario, when, then

from src.lib.config import get_store_reader, get_store_writer
from src.lib.login import get_bearer_authorization_header_value, login_from_cache
from user import get_main_login_user

get_env = get_store_reader()
set_env = get_store_writer()


# To use PyTest parameterized fixtures with BDD, you
# FIRST define the fixture param ('driver_functionality' below),
# THEN define the @scenario (order DOES matter).
# Finally, you inject the driver in the given/when/then functions.
@pytest.mark.driver_functionality('login')
@scenario('carts.feature', 'Get a cart')
def test_carts(shopping_driver):
    pass


@given(
    parsers.re(r"I have cart ID (?P<cart_id>\d+)"),
    converters={"cart_id": int},
)
def given_cart_id(cart_id):
    set_env('cart_id')(cart_id)


@when(
    parsers.re(r"I fetch this cart"),
)
def when_fetch_cart(shopping_driver):
    login_from_cache(get_main_login_user())(shopping_driver)
    cart_id = get_env('cart_id')
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{cart_id}"
    print(f"Getting product {cart_id} from shopping server")
    response = requests.get(
        url=url,
        headers={
            'Content-Type': 'application/json',
            'Authorization': get_bearer_authorization_header_value()
        },
    )
    data = response.json()
    assert data is not None
    set_env('cart_data')(data)


@then(
    parsers.re(r"I get back the cart with ID (?P<cart_id>\d+)"),
    converters={"cart_id": int},
)
def then_get_back_cart_with_id(cart_id):
    data = get_env('cart_data')
    assert data.get('id', None) == cart_id


@then(
    parsers.re(r"A non-empty title"),
)
def then_get_back_cart_with_non_empty_title():
    data = get_env('cart_data')
    assert len(data.get('title', '')) > 0
