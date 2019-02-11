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
    result = testdir.runpytest('-v')
    assert result.ret == 0
    result.stdout.fnmatch_lines([
        '*::test_test PASSED*',
    ])

    # Store test run timestamp
    t0 = os.path.getmtime(timestampfile)

    # Ensure next modification time is far enough away.
    # Do we need this? What's a good value?
    time.sleep(1.1)

    # Rerunning the test should still pass, since we haven't modified anything
    result = testdir.runpytest('-v')
    assert result.ret == 0
    result.stdout.fnmatch_lines([
        '*::test_test PASSED*',
    ])

    # Verify that the test pass was from the cache
    t1 = os.path.getmtime(timestampfile)
    assert "Result should have come from the cache, and rerun skipped" and (t1 == t0)


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
    result = testdir.runpytest()
    assert result.ret == 1
    result.stdout.fnmatch_lines([
        'collected 1 item',
        'test_test.py:5: AssertionError',
    ])

    # Store test run timestamp
    t0 = os.path.getmtime(timestampfile)

    # Ensure next modification time is far enough away.
    # Do we need this? What's a good value?
    time.sleep(1.1)

    # Rerunning the test should still fail, since we haven't modified anything
    result = testdir.runpytest()
    assert result.ret == 1
    result.stdout.fnmatch_lines([
        'collected 1 item',
        'test_test.py:5: AssertionError',
    ])

    # Verify that the test fail was from a rerun
    t1 = os.path.getmtime(timestampfile)
    assert "Test should have been rerun" and (t1 > t0)
