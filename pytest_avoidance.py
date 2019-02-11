# -*- coding: utf-8 -*-

import _pytest.reports


def known_pass(item):
    # FIXME: Actually check the cache
    return False


def fake_pass_report(item, stage):
    # FIXME: Should we indicate somehow this result is from the cache?

    # From pytest_runtest_makereport():
    # https://github.com/pytest-dev/pytest/blob/master/src/_pytest/runner.py
    keywords = {x: 1 for x in item.keywords}

    longrepr = None  # Used for exception info, but since we're passing this should be None

    # From pytest_runtest_makereport():
    # https://github.com/pytest-dev/pytest/blob/master/src/_pytest/runner.py
    sections = []
    for rwhen, key, content in item._report_sections:
        sections.append(("Captured %s %s" % (key, rwhen), content))

    return _pytest.reports.TestReport(
        item.nodeid,
        item.location,
        keywords,
        "pass",
        longrepr,
        stage,
        sections,
        0,
        user_properties=item.user_properties,
    )


def pytest_collection_modifyitems(session, config, items):
    cache_hits = []
    cache_misses = []

    # Filter out known-pass items
    for item in items:
        if known_pass(item):
            cache_hits.append(item)
        else:
            cache_misses.append(item)
    items[:] = cache_misses

    for hit in cache_hits:
        hit.ihook.pytest_runtest_logreport(fake_pass_report(item, "setup"))
        hit.ihook.pytest_runtest_logreport(fake_pass_report(item, "call"))
        hit.ihook.pytest_runtest_logreport(fake_pass_report(item, "teardown"))


def pytest_runtest_setup(item):
    # FIXME: Start coverage tracking

    pass


def pytest_runtest_teardown(item, nextitem):
    # FIXME: Collect coverate into a deps file

    pass
