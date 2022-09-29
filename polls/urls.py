from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("auth-flow/", views.AuthFlowView.as_view(), name="auth-flow"),
    path("task-flow/", views.TaskFlowView.as_view(), name="task-flow"),
    path("auth-token/", views.TokenView.as_view(), name="auth-token"),
    # APIs
    path("api/v1/admin-api/", views.AdminAPIView.as_view(), name="admin-api"),
    path(
        "api/v1/annotation-list/",
        views.AnnotationListAPI.as_view(),
        name="annotation-api",
    ),
    path("api/v1/lock-users/", views.UserLockAPIView.as_view(), name="lock-users-api"),
    path(
        "api/v1/batch-tasks/", views.BatchTasksAPIView.as_view(), name="batch-tasks-api"
    ),
]
