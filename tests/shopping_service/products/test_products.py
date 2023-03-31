from verifit.login import DRIVER, USER, login_from_cache

from driver_get_products_all import all_get_products_drivers
from login_before_test import get_main_user, login_before_test


# Note how we use here a driver defined in another folder.
# For this to work, though, you need that other folder to have
# at least one `test_...` function that Py.Test collects,
# otherwise it will not be in the path and it will fail to find 
# your driver.
#
# We also use a second driver from this folder.
#
# So you can use multiple drivers from multiple folders in a single test
def test_products(select_current_shopping_driver):
    login_from_cache({USER: get_main_user(), DRIVER: login_before_test})
    get_products_driver = select_current_shopping_driver(all_get_products_drivers())
    data = get_products_driver(1)
    assert data.get('id', None) == 1
    assert len(data.get('title', '')) > 0
