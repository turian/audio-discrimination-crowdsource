from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .custom_mixin import CheckUserLockMixin
from .models import Annotation, CurrentBatchEval, CurrentBatchGold, Task
from .utils import batch_selector, check_user_work_permission, present_task_for_user


class IndexView(TemplateView):
    template_name = "polls/index.html"


class HomeView(TemplateView):
    template_name = "polls/home.html"


class ThanksView(TemplateView):
    template_name = "polls/thanks.html"


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

    def check_user_is_locked(self):
        return self.request.user.is_locked


class TaskFlowView(LoginRequiredMixin, CheckUserLockMixin, View):
    template_name = "polls/task_flow.html"

    def get(self, request):
        can_continue, should_rest, _ = check_user_work_permission(request.user)
        if should_rest:
            return redirect("auth-flow")
        elif can_continue:
            # Update user's session start time
            request.user.first_task_of_this_session_performed_at = timezone.now()
            request.user.save()

        if batch_selector():
            # when probability lesss than 90%
            current_batch = CurrentBatchEval.objects.first().current_batch_eval
        else:
            current_batch = CurrentBatchGold.objects.first().current_batch_gold
        all_tasks = current_batch.tasks.all()
        tasks_for_user = all_tasks.exclude(annotation__user=request.user)
        task = tasks_for_user.first()
        context = {"task": task}
        if not task:
            return render(request, self.template_name, context)
        url, task_presentation = present_task_for_user(task)
        context["url"] = url
        context["task_presentation"] = task_presentation
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
        admin_api_url = request.build_absolute_uri("/polls/api/v1/admin-api/")
        token, _ = Token.objects.get_or_create(user=request.user)
        context = {"token": token, "admin_api_url": admin_api_url}
        return render(request, "polls/auth_token.html", context)

    def test_func(self):
        return self.request.user.is_superuser


class AdminAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        return Response({"data": "hello"}, status.HTTP_200_OK)
