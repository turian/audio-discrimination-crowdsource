from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone

from .models import CurrentBatchEval, CurrentBatchGold, Batch, Task, Annotation
from .utils import batch_selector, present_task_for_user

class IndexView(TemplateView):
    template_name = "polls/index.html"

class AuthFlowView(LoginRequiredMixin, View):
    template_name = "polls/auth_flow.html"
    minutes_after_should_rest = 15
    minutes_after_can_continue = 75

    def get(self, request):
        if not request.user.first_task_of_this_session_performed_at:
            # if it's user's first time
            context = {
                "should_rest": False,
                "can_continue": False
                }
            return render(request, self.template_name, context)

        current_time = timezone.now()
        time_diff = current_time - request.user.first_task_of_this_session_performed_at
        time_diff_minutes = time_diff.total_seconds() / 60
        should_rest = time_diff_minutes > self.minutes_after_should_rest and \
                      time_diff_minutes < self.minutes_after_can_continue
        can_continue = time_diff_minutes > self.minutes_after_can_continue
        rest_time = round(self.minutes_after_can_continue - time_diff_minutes) + 1
        context = {
            "should_rest": should_rest,
            "can_continue": can_continue,
            "rest_time": rest_time
        }
        return render(request, self.template_name, context)

class TaskFlowView(LoginRequiredMixin, View):
    template_name = "polls/task_flow.html"

    def get(self, request):
        if batch_selector():
            # when probability lesss than 90%
            current_batch = CurrentBatchEval.objects.first().current_batch_eval
        else:
            current_batch = CurrentBatchGold.objects.first().current_batch_gold
        all_tasks = current_batch.tasks.all()
        tasks_for_user = all_tasks.exclude(annotation__user=request.user)
        task = tasks_for_user.first()
        context = { "task": task }
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
            annotations=annotation_choice
        )
        return redirect("auth-flow")