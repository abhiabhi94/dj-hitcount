Installation and Usage
======================

Install using ``pip``.

.. code:: sh

    $ python -m pip install dj-hitcount

If you want, you may install it from the source, grab the source code and run ``setup.py``.

.. code:: sh

    $ git clone git://github.com/abhiabhi94/dj-hitcount.git
    $ cd dj-hitcount
    $ python setup.py install


Add ``dj-hitcount`` to your ``INSTALLED_APPS``::

    # settings.py
    INSTALLED_APPS = (
        ...
        'hitcount'
    )

View the :doc:`additional settings section </settings>` for a list of the available settings that can be configured.

For a working implementation, you can view the `example project`_ on Github.

Counting Hits
-------------

The main business-logic for evaluating and counting a `Hit` is done in ``hitcount.mixins.HitCountViewMixin.hit_count()``. You can use this static method directly in your own Views or you can use one of the Views packaged with this app.

 * `HitCountJSONView`_: a JavaScript implementation which moves the business-logic to an Ajax View and hopefully speeds up page load times and eliminates some bot-traffic
 * `HitCountDetailView`_: which provides a wrapper from  Django's generic ``DetailView`` and allows you to process the Hit as the view is loaded

HitCountMixin
^^^^^^^^^^^^^

This mixin can be used in your own class-based views or you can call the ``hit_count()`` method directly.   The method takes two arguments, a ``HttpRequest`` and ``HitCount`` object it will return a namedtuple: ``UpdateHitCountResponse(hit_counted=Boolean, hit_message='Message')``.

``hit_counted`` will be ``True`` if the hit was counted and ``False`` otherwise.  ``hit_message`` will indicate by what means the Hit was either counted or ignored.

It works like this. ::

    from hitcount.models import HitCount
    from hitcount.mixins import HitCountViewMixin

    # first get the related HitCount object for your model object
    hit_count = HitCount.objects.get_for_object(your_model_object)

    # next, you can attempt to count a hit and get the response
    # you need to pass it the request object as well
    hit_count_response = HitCountViewMixin.hit_count(request, hit_count)

    # your response could look like this:
    # UpdateHitCountResponse(hit_counted=True, hit_message='Hit counted: session key')
    # UpdateHitCountResponse(hit_counted=False, hit_message='Not counted: session key has active hit')

To see this in action see the `views`_.py code.

HitCountJSONView
^^^^^^^^^^^^^^^^

The ``hitcount.views.HitCountJSONView`` can be used to handle an AJAX POST request.  Dj-hitcount comes with a bundled `jQuery plugin`_ for speeding up the ``$.post`` process by handling the retrieval of the CSRF token for you.

If you wish to use the ``HitCountJSONView`` in your project you first need to update your ``urls.py`` file to include the following::

    # urls.py
    from django.urls import path

    urlpatterns = [
        ...
        path('hitcount/', include('hitcount.urls', namespace='hitcount')),
    ]

Next, you will need to add the JavaScript Ajax request to your template.  To do this, use the ``{% get_hit_count_js_variables for post as [var_name] %}`` template tag to get the ``ajax_url`` and ``hitcount_pk`` for your object.  The ``hitcount_pk`` is needed for POST-ing to the ``HitCountJSONView``.

Here is an example of how all this might work together with the bundled `jQuery plugin`_.  It is taken from the `example project`_ and the jQuery can be modified to suit your needs.  In the example below it simply updates the template with the ``HitCountJSONView`` response after the Ajax call is complete.

.. code:: jinja

    {% load staticfiles %}
    <script src="{% static 'hitcount/jquery.postcsrf.js' %}"></script>

    {% load hitcount_tags %}
    {% get_hit_count_js_variables for post as hitcount %}
    <script type="text/javascript">
    jQuery(document).ready(function($) {
      // use the template tags in our JavaScript call
      $.postCSRF("{{ hitcount.ajax_url }}", { hitcountPK : "{{ hitcount.pk }}" })
        .done(function(data){
          $('<i />').text(data.hit_counted).attr('id','hit-counted-value').appendTo('#hit-counted');
          $('#hit-response').text(data.hit_message);
      }).fail(function(data){
          console.log('POST failed');
          console.log(data);
      });
    });
    </script>

HitCountDetailView
^^^^^^^^^^^^^^^^^^

The ``HitCountDetailView`` can be used to do the business-logic of counting the hits by setting ``count_hit=True``.  See the `views`_ section for more information about what else is added to the template context with this view.

Here is an example implementation from the `example project`_::

    from hitcount.views import HitCountDetailView

    class PostCountHitDetailView(HitCountDetailView):
        model = Post        # your model goes here
        count_hit = True    # set to True if you want it to try and count the hit

.. note:: Unlike the JavaScript implementation (above), this View will do all the HitCount processing *before* the content is delivered to the user; if you have a large dataset of Hits or exclusions, this could slow down page load times.  It will also be triggered by web crawlers and other bots that may not have otherwise executed the JavaScript.

Displaying Hits
---------------

There are different methods for *displaying* hits:

* `Template Tags`_: provide a robust way to get related counts.
* `Views`_: allows you to wrap a class-based view and inject additional context into your template.
* :ref:`Models<Models>`: can have a generic relation to their respective ``HitCount``.

Template Tags
^^^^^^^^^^^^^

For a more granular approach to viewing the hits for a related object you can use the ``get_hit_count`` template tag.

::

    # remember to load the tags first
    {% load hitcount_tags %}

    # Return total hits for an object:
    {% get_hit_count for [object] %}

    # Get total hits for an object as a specified variable:
    {% get_hit_count for [object] as [var] %}

    # Get total hits for an object over a certain time period:
    {% get_hit_count for [object] within ["days=1,minutes=30"] %}

    # Get total hits for an object over a certain time period as a variable:
    {% get_hit_count for [object] within ["days=1,minutes=30"] as [var] %}

Views
^^^^^

The ``hitcount.views.HitCountDetailView`` extends Django's generic ``DetailView`` and injects an additional context variable ``hitcount``.

::

    {# the primary key for the hitcount object #}
    {{ hitcount.pk }}

    {# the total hits for the object #}
    {{ hitcount.total_hits }}

If you have set ``count_hit=True`` (see: `HitCountDetailView`_) two additional variables will be set.

::

    {# whether or not the hit for this request was counted (true/false) #}
    {{ hitcount.hit_counted }}

    {# the message form the UpdateHitCountResponse #}
    {{ hitcount.hit_message }}


.. _jQuery plugin: https://github.com/abhiabhi94/dj-hitcount/blob/main/hitcount/static/hitcount/jquery.postcsrf.js

.. _example project: https://github.com/abhiabhi94/dj-hitcount/blob/main/tests/blog/

.. _views: https://github.com/abhiabhi94/dj-hitcount/blob/main/hitcount/views.py
