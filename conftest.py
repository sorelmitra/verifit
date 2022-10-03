import sys

sys.path.append("./src/lib")

from collected_tests import CollectedTests


def pytest_collection_finish(session):
    """
    Called after collection of tests has finished.
    """
    for item in session.items:
        CollectedTests.names.append(item.originalname)

