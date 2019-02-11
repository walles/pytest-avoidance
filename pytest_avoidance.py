# -*- coding: utf-8 -*-

import pytest


def pytest_collection_modifyitems(session, config, items):
    # FIXME: Filter out known-pass items

    # FIXME: For all filtered-out item:
    # item.ihook.pytest_runtest_logreport(setup_report)
    # item.ihook.pytest_runtest_logreport(call_report)
    # item.ihook.pytest_runtest_logreport(teardown_report)

    pass


def pytest_runtest_setup(item):
    # FIXME: Start coverage tracking

    pass


def pytest_runtest_teardown(item, nextitem):
    # FIXME: Collect coverate into a deps file

    pass
