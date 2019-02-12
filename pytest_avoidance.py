# -*- coding: utf-8 -*-

import _pytest.reports
import _pytest.nodes

import pytest

import coverage
import hashlib
import errno
import sys
import os

# FIXME: Put this where .pytest_cache is, how do they find their location?
CACHEROOT = '/tmp/FIXME/.pytest-avoidance'


# Global state
have_cache_hits = False


def get_vm_identifier():
    """
    Returns a Python VM identifier "python-1.2.3-HASH", where the
    HASH is a hash of the VM contents and its location on disk.
    """

    (major, minor, micro, releaselevel, serial) = sys.version_info

    # From: https://stackoverflow.com/a/3431838/473672
    hash_md5 = hashlib.md5()
    with open(sys.executable, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    hash_md5.update(sys.executable.encode('utf-8'))
    hash = hash_md5.hexdigest()

    return "python-{}.{}.{}-{}".format(major, minor, micro, hash)


VM_IDENTIFIER = get_vm_identifier()


# From: https://stackoverflow.com/a/600612/473672
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_depsfile_name(item):
    # Dependencies file naming scheme:
    # .pytest-avoidance/<VM-identifier>/<path to .py file>/testname.deps

    # From: https://github.com/pytest-dev/pytest/blob/9f9f6ee48beba8bbf0911e458590aa67b45bd867/src/_pytest/nodes.py#L290
    test_file, lineno = _pytest.nodes.get_fslocation_from_item(item)
    if test_file[1] == ':':
        # Somebody on a Windows box, please test this
        test_file = test_file.replace(':', '/', 1)
    if test_file[0] == '/':
        # Starting the path with '/' would mess up os.path.join()
        test_file = test_file[1:]

    cachedir = os.path.join(CACHEROOT, VM_IDENTIFIER, test_file)

    mkdir_p(cachedir)
    depsfile_name = os.path.join(cachedir, item.name + ".deps")

    return depsfile_name


def has_cached_success(item):
    depsfile_name = get_depsfile_name(item)
    if not os.path.isfile(depsfile_name):
        # Nothing cached for this test
        print("Cache entry doesn't exist, no hit: " + depsfile_name)
        return False

    cache_timestamp = os.path.getmtime(depsfile_name)
    with open(depsfile_name, 'r') as depsfile:
        for depsline in depsfile:
            filename = depsline.rstrip()
            if not os.path.isfile(filename):
                # Dependency is gone
                print("Dependency gone, no hit: " + filename)
                return False

            file_timestamp = os.path.getmtime(filename)

            if file_timestamp > cache_timestamp:
                # Dependency updated
                print("Dependency updated, no hit: " + filename)
                return False

    # No mismatch found for this test, it's a cache hit!
    return True


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
        "passed",  # Magic constant: https://github.com/pytest-dev/pytest/blob/7dcd9bf5add337686ec6f2ee81b24e8424319dba/src/_pytest/reports.py#L92
        longrepr,
        stage,
        sections,
        0,
        user_properties=item.user_properties,
    )


def pytest_collection_modifyitems(session, config, items):
    global have_cache_hits
    cache_hits = []
    cache_misses = []

    # Filter out known-pass items
    for item in items:
        if has_cached_success(item):
            have_cache_hits = True
            cache_hits.append(item)
        else:
            cache_misses.append(item)
    items[:] = cache_misses

    for hit in cache_hits:
        # Log "setup" and "teardown" here as well?
        hit.ihook.pytest_runtest_logreport(report=fake_pass_report(item, "call"))


def pytest_runtest_setup(item):
    # Start coverage tracking
    cov = coverage.Coverage()
    item['avoidance-coverage'] = cov
    cov.start()


def pytest_runtest_teardown(item, nextitem):
    # Collect coverate into a deps file
    cov = item['avoidance-coverage']
    cov.stop()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    if call.excinfo:
        # We don't cache failures
        return

    cov = item['avoidance-coverage']
    coverage_data = cov.get_data()
    item['avoidance-coverage'] = None

    with open(get_depsfile_name(item), "w") as depsfile:
        for filename in coverage_data.measured_files():
            depsfile.write("%s\n" % (filename,))

    return None


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 5 and have_cache_hits:
        # Exit status 5 means no tests were run. If we have cache hits,
        # this means we hit all tests, and we should report all-tests-run.
        session.exitstatus = 0
