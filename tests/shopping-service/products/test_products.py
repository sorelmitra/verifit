
from verifit.driver import get_driver
from verifit.login import login_main_user_from_cache


# Note how we use here a driver defined in another folder.
# For this to work, though, you need that other folder to have
# at least one `test_...` function that Py.Test collects,
# otherwise it will not be in the path and it will fail to find 
# your driver.
#
# We also use a second driver from this folder.
#
# So you can use multiple drivers from multiple folders in a single test
def test_products(shopping_driver_name):
    login_main_user_from_cache(shopping_driver_name)
    data = get_driver(shopping_driver_name)('get-products')(1)
    assert data.get('id', None) == 1
    assert len(data.get('title', '')) > 0
