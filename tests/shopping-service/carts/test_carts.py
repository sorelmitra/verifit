from pytest_bdd import given, parsers, scenario, when, then

from verifit.config import get_store_reader, get_store_writer
from verifit.login import login_main_user_from_cache
from verifit.retrieve import LOG_PREFIX, retrieveHttp

get_env = get_store_reader()
set_env = get_store_writer()


# To use PyTest parameterized fixtures with BDD, you
# FISRT define the @scenario (order DOES matter).
# THEN, you inject the driver name in the given/when/then functions.
# This function is not actually called, anything you put into it
# is ignored.
@scenario('carts.feature', 'Get a cart')
def test_carts(shopping_driver_name):
    pass


@given(
    parsers.re(r"I have cart ID (?P<cart_id>\d+)"),
    converters={"cart_id": int},
)
def given_cart_id(cart_id):
    set_env('cart_id')(cart_id)


# Here, we inject the driver name again.  Because we injected it
# into the actual test function above, this works.
@when(
    parsers.re(r"I fetch this cart"),
)
def when_fetch_cart(shopping_driver_name):
    login_main_user_from_cache(shopping_driver_name)
    cart_id = get_env('cart_id')
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{cart_id}"
    data = retrieveHttp(url)({
        LOG_PREFIX: f"Get cart product {cart_id}",
    })
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
