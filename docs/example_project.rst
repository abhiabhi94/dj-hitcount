Real World Example
==================

There is an `example project`_ that tries to demonstrate the functionality of this app.  You can get it working using the Django development server.  Be sure to run this inside your own ``virtualenv``::

    $ git clone git@github.com:abhiabhi94/dj-hitcount.git
    $ pip install -r dev-requirements.txt
    $ python -m django --settings=test.settings migrate  # will load some data fixtures for you
    $ python -m django --settings=test.settings createsuperuser  # for access to the admin portion
    $ python -m django --settings=test.settings runserver        # should be all set!

When you are ready to work on your own site, check out the :doc:`installation` and :doc:`settings` sections.

.. _example project: https://github.com/abhiabhi94/dj-hitcount/blob/main/tests/blog/
