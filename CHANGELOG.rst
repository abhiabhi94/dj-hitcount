Changelog
=========

Unreleased
----------

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

    - removed additional dependency of ``django-etc``.

    - ``hitcount.views.update_hit_count_ajax`` that was to be removed in ``django-hitcount`` ``1.2`` has been removed. Use ``hitcount.views.HitCountJSONView`` instead.

    - ``hitcount.views._update_hit_count`` that was to be removed in ``django-hitcount`` ``1.2`` has been removed. Use ``hitcount.mixins.HitCountViewMixin.hit_count`` instead.


.. _boolean-trap: https://ariya.io/2011/08/hall-of-api-shame-boolean-trap
