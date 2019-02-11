import os.path
import time


def test_reruns_test_on_test_change(testdir):
    # Create a passing test
    testdir.makepyfile(test_test="""
        def test_test():
            assert True
    """)

    # Verify that the test suite passed
    assert testdir.runpytest().ret == 0

    # Update the test to fail
    testdir.makepyfile(test_test="""
        def test_test():
            assert False
    """)

    # Verify that the test suite failed after we changed it
    assert testdir.runpytest().ret != 0


def test_skips_rerun_on_pass(testdir):
    # Create a test that stores its runtime on disk
    timestampfile = str(testdir.tmpdir.join("timestampfile"))
    testdir.makepyfile(test_test="""
        def test_test():
            with open("{}", "w") as text_file:
                text_file.write("Johan")

            assert True
    """.format(timestampfile))

    # Test should pass
    assert testdir.runpytest().ret == 0

    # Store test run timestamp
    t0 = os.path.getmtime(timestampfile)

    # Ensure next modification time is far enough away.
    # Do we need this? What's a good value?
    time.sleep(1.1)

    # Rerunning the test should still pass, since we haven't modified anything
    assert testdir.runpytest().ret == 0

    # FIXME: Verify that pytest says one (1) test was run

    # Verify that the test pass was from the cache
    t1 = os.path.getmtime(timestampfile)
    assert t1 == t0


def test_do_rerun_on_fail(testdir):
    # Create a test that stores its runtime on disk
    timestampfile = str(testdir.tmpdir.join("timestampfile"))
    testdir.makepyfile(test_test="""
        def test_test():
            with open("{}", "w") as text_file:
                text_file.write("Johan")

            assert False
    """.format(timestampfile))

    # Test should fail
    assert testdir.runpytest().ret == 1

    # Store test run timestamp
    t0 = os.path.getmtime(timestampfile)

    # Ensure next modification time is far enough away.
    # Do we need this? What's a good value?
    time.sleep(1.1)

    # Rerunning the test should still fail, since we haven't modified anything
    assert testdir.runpytest().ret == 1

    # FIXME: Verify that pytest says one (1) test was run

    # Verify that the test fail was from a rerun
    t1 = os.path.getmtime(timestampfile)
    assert t1 > t0


def test_bar_fixture(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_sth(bar):
            assert bar == "europython2015"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--foo=europython2015',
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'avoidance:',
        '*--foo=DEST_FOO*Set the value for the fixture "bar".',
    ])


def test_hello_ini_setting(testdir):
    testdir.makeini("""
        [pytest]
        HELLO = world
    """)

    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def hello(request):
            return request.config.getini('HELLO')

        def test_hello_world(hello):
            assert hello == 'world'
    """)

    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_hello_world PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
