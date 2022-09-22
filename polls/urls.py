from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("auth-flow/", views.AuthFlowView.as_view(), name="auth-flow"),
    path("task-flow/", views.TaskFlowView.as_view(), name="task-flow"),
    path("auth-token/", views.TokenView.as_view(), name="auth-token"),
    path("thank-you/", views.ThanksView.as_view(), name="thank-you"),
    # APIs
    path("api/v1/admin-api/", views.AdminAPIView.as_view()),
]
