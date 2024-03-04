import pytest


# command line option
def pytest_addoption(parser):
    parser.addoption("--host", action="store")
    parser.addoption("--prefix", action="store")
    parser.addoption("--scheme", action="store")


# creating a fixture to use the command line option.
@pytest.fixture(autouse=True)
def host(request):
    return request.config.getoption("--host")


@pytest.fixture(autouse=True)
def prefix(request):
    return request.config.getoption("--prefix")


@pytest.fixture(autouse=True)
def scheme(request):
    return request.config.getoption("--scheme")
