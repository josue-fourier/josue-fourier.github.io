from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.MainViews.as_view(), name="main"),
]
