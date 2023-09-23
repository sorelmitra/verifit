from pytest_bdd import given, parsers, scenario, when, then

from verifit.config import get_store_reader, get_store_writer
from verifit.login import login_from_cache
from verifit.retrieve import retrieve_http

from tests.shopping_service.login.shopping_service_login import shopping_get_main_user, shopping_login

get_env = get_store_reader()
set_env = get_store_writer()


@scenario('carts.feature', 'Get a cart')
def test_carts():
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
def when_fetch_cart():
    login_from_cache(driver=shopping_login, **shopping_get_main_user())
    cart_id = get_env('cart_id')
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{cart_id}"
    data = retrieve_http(url=url, log_prefix=f"Get cart product {cart_id}")
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
