from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from rest_framework import generics, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .custom_mixin import CheckUserLockMixin
from .models import Annotation, CurrentBatchEval, CurrentBatchGold, Experiment, Task
from .serializers import AnnotationSerializer, BatchTaskSerializer
from .utils import (
    batch_selector,
    check_user_work_permission,
    parse_data_for_admin_experiment,
    present_task_for_user,
)


class IndexView(TemplateView):
    template_name = "polls/index.html"


class HomeView(TemplateView):
    template_name = "polls/home.html"


class AuthFlowView(LoginRequiredMixin, CheckUserLockMixin, View):
    template_name = "polls/auth_flow.html"

    def get(self, request):
        can_continue, should_rest, rest_time = check_user_work_permission(request.user)
        context = {
            "can_continue": can_continue,
            "should_rest": should_rest,
            "rest_time": rest_time,
        }
        return render(request, self.template_name, context)


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "polls/admin_dashboard.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        experiments = Experiment.objects.all()
        context = {
            "experiments": experiments,
        }
        return render(request, self.template_name, context)


class AdminExperimentView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "polls/admin_experiment.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, experiment_id):
        try:
            experiment = Experiment.objects.get(id=experiment_id)
            batches = experiment.experiment_type.batches.all().order_by("-is_gold")
            data_list = parse_data_for_admin_experiment(batches)
            context = {"experiment": experiment, "data_list": data_list}
        except Experiment.DoesNotExist:
            context = {
                "error_message": "The Experiment with provided ID does not exist"
            }
        return render(request, self.template_name, context)


class TaskFlowView(CheckUserLockMixin, LoginRequiredMixin, View):
    template_name = "polls/task_flow.html"

    def get(self, request):
        can_continue, should_rest, _ = check_user_work_permission(request.user)
        if should_rest:
            return redirect("auth-flow")

        if can_continue:
            # Update user's session start time
            request.user.first_task_of_this_session_performed_at = timezone.now()
            request.user.save()

        current_batch = ""
        if batch_selector():
            current_batch_eval = CurrentBatchEval.objects.first()
            current_batch = (
                current_batch_eval.current_batch_eval if current_batch_eval else ""
            )
        else:
            current_batch_gold = CurrentBatchGold.objects.first()
            current_batch = (
                current_batch_gold.current_batch_gold if current_batch_gold else ""
            )

        context = {}
        if current_batch:
            tasks_for_user = current_batch.tasks.exclude(annotation__user=request.user)
            task = tasks_for_user.first()
            if task:
                url, task_presentation = present_task_for_user(task)
                context = {
                    "task": task,
                    "url": url,
                    "task_presentation": task_presentation,
                }
        return render(request, self.template_name, context)

    def post(self, request):
        annotation_choice = request.POST.get("annotationOption")
        task_pk = request.POST.get("taskPk")
        task_presentation = request.POST.get("taskPresentation")
        Annotation.objects.create(
            user=request.user,
            task=Task.objects.get(pk=task_pk),
            annotated_at=timezone.now(),
            task_presentation=task_presentation,
            annotations=annotation_choice,
        )
        return redirect("task-flow")

    def check_user_is_locked(self):
        return self.request.user.is_locked


class TokenView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        admin_api = request.build_absolute_uri(reverse("admin-api-url"))
        annotation_api = request.build_absolute_uri(reverse("annotation-api"))
        lock_users_api = request.build_absolute_uri(reverse("lock-users-api"))
        batch_tasks_api = request.build_absolute_uri(reverse("batch-tasks-api"))
        token, _ = Token.objects.get_or_create(user=request.user)
        context = {
            "token": token,
            "admin_api": admin_api,
            "annotation_api": annotation_api,
            "lock_users_api": lock_users_api,
            "batch_tasks_api": batch_tasks_api,
        }
        return render(request, "polls/auth_token.html", context)

    def test_func(self):
        return self.request.user.is_superuser


class AdminAPIView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        return Response({"data": "hello"}, status.HTTP_200_OK)

    def test_func(self):
        return self.request.user.is_superuser


class ThanksView(TemplateView):
    template_name = "polls/thanks.html"


class AnnotationListAPI(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserLockAPIView(APIView):
    def post(self, request):
        user_ids = request.data.get("users", list())
        user_not_found = list()
        for id in user_ids:
            try:
                user = get_user_model().objects.get(id=id)
                user.is_locked = True
                user.save()
            except get_user_model().DoesNotExist:
                user_not_found.append(id)
        return Response({"users_not_found": user_not_found}, status.HTTP_200_OK)


class BatchTasksAPIView(APIView):
    allowed_methods = ["POST"]

    def post(self, request):
        serializer = BatchTaskSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            batch = serializer.save()
            print(batch)  # print is a placeholder to fulfil flake8 needs.
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def test_func(self):
        return self.request.user.is_superuser


class AdminManagementView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser
