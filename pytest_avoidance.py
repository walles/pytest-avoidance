# -*- coding: utf-8 -*-

import _pytest.reports
import _pytest.nodes

import pytest

import coverage
import hashlib
import errno
import sys
import os
import re

CACHEROOT = None

PARAMETERS_RE = re.compile(r'\[([^]]+)\]')


# Global state
have_cache_hits = False


def pytest_configure(config):
    global CACHEROOT
    CACHEROOT = os.path.join(str(config.rootdir), '.pytest-avoidance')


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


def censor_parameters(itemname):
    # type: (str) -> str
    match = PARAMETERS_RE.search(itemname)
    if not match:
        return itemname

    censoring = hashlib.md5(bytearray(itemname, encoding="utf-8", errors="replace")).hexdigest()
    return PARAMETERS_RE.sub('[' + censoring + ']', itemname)


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

    # This should have been set up in pytest_configure() (see above)
    assert CACHEROOT is not None

    cachedir = os.path.join(CACHEROOT, VM_IDENTIFIER, test_file)

    mkdir_p(cachedir)

    readme = os.path.join(CACHEROOT, 'README.txt')
    if not os.path.isfile(readme):
        with open(readme, "w") as readme_file:
            readme_file.write("See: https://github.com/walles/pytest-avoidance\n")

    depsfile_name = os.path.join(cachedir, censor_parameters(item.name) + ".deps")
    return depsfile_name


def has_cached_success(item):
    depsfile_name = get_depsfile_name(item)
    if not os.path.isfile(depsfile_name):
        # Nothing cached for this test
        return False

    cache_timestamp = os.path.getmtime(depsfile_name)
    with open(depsfile_name, 'r') as depsfile:
        for depsline in depsfile:
            filename = depsline.rstrip()
            if not os.path.isfile(filename):
                # Dependency is gone
                return False

            file_timestamp = os.path.getmtime(filename)

            if file_timestamp > cache_timestamp:
                # Dependency updated
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

    fake_report = _pytest.reports.TestReport(
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

    # Log "setup" and "teardown" here as well?
    item.ihook.pytest_runtest_logreport(report=fake_report)


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
        fake_pass_report(hit, "call")


def pytest_runtest_setup(item):
    # Start coverage tracking
    cov = coverage.Coverage()
    item.avoidance_coverage = cov
    cov.start()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    if call.when != "call":
        # Coverage should be collected only in conjunction with actually running the test
        return None

    # Collect coverate into a deps file
    cov = item.avoidance_coverage
    cov.stop()

    if call.excinfo:
        # We don't cache failures
        return

    coverage_data = cov.get_data()
    item.avoidance_coverage = None

    with open(get_depsfile_name(item), "w") as depsfile:
        for filename in coverage_data.measured_files():
            depsfile.write("%s\n" % (filename,))

    return None


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 5 and have_cache_hits:
        # Exit status 5 means no tests were run. If we have cache hits,
        # this means we hit all tests, and we should report all-tests-run.
        session.exitstatus = 0
