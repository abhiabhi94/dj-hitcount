Changelog
=========

1.2.0
-----

- Confirm support for python ``3.10`` (`#19`_).
- Add a setting for limiting hits per single browser session (`#16`_).
- Respect the setting for limiting hits per IP before counting a hit (`#18`_).

.. _#18: https://github.com/abhiabhi94/dj-hitcount/pull/18/
.. _#16: https://github.com/abhiabhi94/dj-hitcount/pull/16/
.. _#19: https://github.com/abhiabhi94/dj-hitcount/pull/19/

1.1.0
-----

- Confirm support for python ``3.10-dev`` (`#11`_).
- Optimize query for saving of increased and decreased hits(`#10`_).
- Prevent compiling of ``regex`` for IP detection on every import of ``hitcount.utils`` (`#8`_)

.. _#8: https://github.com/abhiabhi94/dj-hitcount/pull/8/
.. _#10: https://github.com/abhiabhi94/dj-hitcount/pull/10/
.. _#11: https://github.com/abhiabhi94/dj-hitcount/pull/11/

1.0.1
-----

- Fix saving of anonymous sessions(`#4`_).

.. _#4: https://github.com/abhiabhi94/dj-hitcount/pull/4/

1.0.0
-----

- Bring back project to life.
- Change in project structure
    - ``signals``
        - ``delete_hit_count`` from ``hitcount.models`` has been moved to ``hitcount.signals``.
            - The argument ``save_hitcount`` to the function ``delete_hit_count_handler`` (this process the signal ``delete_hit_count``) is now ``keyword-only``. The earlier design pattern was a case of `boolean-trap`_.
    - ``mixins``
        - ``HitCountMixin`` from ``hitcount.models`` has been renamed as ``HitCountModelMixin`` and moved to ``hitcount.mixins``.
        - ``HitCountMixin`` from ``hitcount.views`` has been renamed as ``HitCountViewMixin`` and moved to ``hitcount.mixins``.

    - ``models``
        - ``BlackListIP`` renamed to ``BlockedIP``.
        - ``BlackListUserAgent`` renamed to ``BlockedUserAgent``.
        - The ``ip`` field for ``Hit`` model has been made optional. This hopefully makes the project GDPR compliant. Please open an issue if still isn't.
            - To maintain backwards compatibility with ``django-hitcount``, an additional setting :ref:`HITCOUNT_USE_IP<hitcount_use_ip>` has been added.
    - ``views``
        - ``hitcount.views.update_hit_count_ajax`` that was to be removed in ``django-hitcount`` ``1.2`` has been removed. Use ``hitcount.views.HitCountJSONView`` instead.

        - ``hitcount.views._update_hit_count`` that was to be removed in ``django-hitcount`` ``1.2`` has been removed. Use ``hitcount.mixins.HitCountViewMixin.hit_count`` instead.

    - removed additional dependency of ``django-etc``.
    - added additional unit tests. Test coverage is now ``100%``.


.. _boolean-trap: https://ariya.io/2011/08/hall-of-api-shame-boolean-trap
