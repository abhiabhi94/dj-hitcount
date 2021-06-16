Contributing to DJ HitCount
===========================

There are many ways to contribute to the project. You may improve the documentation, address a bug, add some feature to the code or do something else. All sort of contributions are welcome.


Development
-----------

To start development on this project, fork this repository and follow the following instructions.

.. code:: sh

    # clone the forked repository
    $ git clone YOUR_FORKED_REPO_URL

    # create a virtual environment
    $ python3 -m venv venv
    # activate the virtual environment(unix users)
    $ . venv/bin/activate
    # activate the virtual environment(window users)
    $ venv\Scripts\activate
    # install dependencies
    (venv) $ pip install -e . Django -r dev-requirements.txt pre-commit
    # migrate the migrations to the database and also creates some placeholder data
    (venv) $ python manage.py migrate
    # start the development server
    (venv) $ python manage.py runserver


Testing
-------

To run tests against a particular ``python`` and ``django`` version installed inside your virtual environment, you may use:

.. code:: sh

    (venv) $ pytest


This skips the ``selenium`` tests which are a bit slow to run. To run them as well use

.. code:: sh

    (venv) $ pytest --runslow

You may have to install ``firefox`` and `gecko-driver`_ to run these successfully.

To run tests against all supported ``python`` and ``django`` versions, you may run:

.. code:: sh

    # install dependency
    (venv) $ pip install tox
    # run tests
    (venv) $ tox


.. _gecko-driver: https://github.com/mozilla/geckodriver
