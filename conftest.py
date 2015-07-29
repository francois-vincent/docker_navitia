# encoding: utf-8

import pytest


def pytest_addoption(parser):
    parser.addoption("--nobuild", action="store_true", default=False,
        help="do not build container but fabric it")
    parser.addoption("--nofabric", action="store_true", default=False,
        help="do not build container but create it")
    parser.addoption("--nocreate", action="store_true", default=False,
        help="do not build nor create container, restart it via fabric")
    parser.addoption("--norestart", action="store_true", default=False,
        help="do not build nor create container, just start it")
    parser.addoption("--commit", action="store_true", default=False,
        help="commit containers")


@pytest.fixture
def nobuild(request):
    return request.config.getoption("--nobuild")

@pytest.fixture
def nofabric(request):
    return request.config.getoption("--nofabric")

@pytest.fixture
def nocreate(request):
    return request.config.getoption("--nocreate")

@pytest.fixture
def norestart(request):
    return request.config.getoption("--norestart")

@pytest.fixture
def commit(request):
    return request.config.getoption("--commit")
