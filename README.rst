================
pytest-avoidance
================

.. image:: https://img.shields.io/pypi/v/pytest-avoidance.svg
    :target: https://pypi.org/project/pytest-avoidance
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-avoidance.svg
    :target: https://pypi.org/project/pytest-avoidance
    :alt: Python versions

.. image:: https://travis-ci.com/walles/pytest-avoidance.svg?branch=master
    :target: https://travis-ci.com/walles/pytest-avoidance
    :alt: See Build Status on Travis CI

Makes pytest skip tests that don't need rerunning


How pytest-avoidance avoids tests
---------------------------------
Each test is run with coverage enabled.

After running each test, ``pytest-avoidance`` stores a list of which files
each test touched.

The next time a test run is requested, ``pytest-avoidance`` checks if any
of the files covered by this test have changed. If none have, the test can
be delared to ``PASS``, even without running it!

``pytest-avoidance`` does not cache failures. Mostly because AFAIU
``bazel`` doesn't either, and I'm just guessing they have good reasons not
to...


Installation
------------

You can install "pytest-avoidance" via `pip`_ from `PyPI`_::

    $ pip install pytest-avoidance


Issues
------
If you encounter any problems, please `file an issue`_ along with a detailed
description.


Contributing
------------
Contributions are very welcome. Please run tests before making PRs:

    $ tox --parallel=auto --skip-missing-interpreters=true


Releasing a new Version
-----------------------
1. Do ``git tag | cat`` and think about what the next version number should be.
2. Do ``git tag --annotate 1.2.3`` to set the next version number. The
   text you write for this tag will show up as the release description on Github,
   write something nice! And remember that the first line is the subject line for
   the release.
3. ``tox -e pypi``
4. ``git push --tags``

Your release should now be visible on the `pytest-avoidance page on Pypi`_.


License
-------
Distributed under the terms of the `MIT`_ license, "pytest-avoidance" is free
and open source software.


----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with
`@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/walles/pytest-avoidance/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
.. _pytest-avoidance page on Pypi: https://pypi.org/project/pytest-avoidance
