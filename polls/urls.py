from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("auth-flow/", views.AuthFlowView.as_view(), name="auth-flow"),
]
