from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("auth-flow/", views.AuthFlowView.as_view(), name="auth-flow"),
    path("task-flow/", views.TaskFlowView.as_view(), name="task-flow"),
    path("auth-token/", views.TokenView.as_view(), name="auth-token"),
    path("thank-you/", views.ThanksView.as_view(), name="thank-you"),
    path("lock/<int:user_id>/", views.LockUserView.as_view(), name="lock-user"),
    path(
        "admin-dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"
    ),
    path(
        "admin-experiment/<int:experiment_id>/",
        views.AdminExperimentView.as_view(),
        name="admin_experiment",
    ),
    path(
        "create-annotation/",
        views.CreateAnnotation.as_view(),
        name="create_annotation",
    ),
    path(
        "admin-management/",
        views.AdminManagementView.as_view(),
        name="admin_management",
    ),
    path(
        "delete-annotator/<int:annotator_id>/",
        views.DeleteAnnotator.as_view(),
        name="perform-delete",
    ),
    # APIs
    path("api/v1/admin-api/", views.AdminAPIView.as_view(), name="admin-api-url"),
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
