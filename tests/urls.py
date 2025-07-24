# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import include
from django.urls import path

from blog import views

admin.autodiscover()

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("generic-detail-view-ajax/<int:pk>/", views.PostDetailJSONView.as_view(), name="ajax"),
    path("hitcount-detail-view/<int:pk>/", views.PostDetailView.as_view(), name="detail"),
    path("hitcount-detail-view-count-hit/<int:pk>/", views.PostCountHitDetailView.as_view(), name="detail-with-count"),
    # for our built-in ajax post view
    path("hitcount/", include("hitcount.urls", namespace="hitcount")),
]

urlpatterns.append(path("admin/", admin.site.urls))
