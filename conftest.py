# encoding: utf-8

import pytest


def pytest_addoption(parser):
    parser.addoption("--build", action="store_true", default=False,
                     help="build image")
    parser.addoption("--fabric", action="store_true", default=False,
                     help="apply fabric's task deploy_from_scratch")
    parser.addoption("--create", action="store_true", default=False,
                     help="create container from image")
    parser.addoption("--commit", action="store_true", default=False,
                     help="commit container")
    parser.addoption("--restart", action="store_true", default=False,
                     help="restart container")


@pytest.fixture
def build(request):
    return request.config.getoption("--build")

@pytest.fixture
def fabric(request):
    return request.config.getoption("--fabric")

@pytest.fixture
def create(request):
    return request.config.getoption("--create")

@pytest.fixture
def commit(request):
    return request.config.getoption("--commit")

@pytest.fixture
def restart(request):
    return request.config.getoption("--restart")
