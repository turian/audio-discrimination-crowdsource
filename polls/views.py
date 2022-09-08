from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone

class IndexView(TemplateView):
    template_name = "polls/index.html"

class AuthFlowView(LoginRequiredMixin, View):
    template_name = "polls/auth_flow.html"
    min_time = 900
    max_time = 4500
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
        time_diff_seconds = time_diff.total_seconds()
        should_rest = time_diff_seconds > self.min_time and time_diff_seconds < self.max_time
        can_continue = time_diff_seconds > self.max_time
        rest_time = round((self.max_time - time_diff_seconds) / 60) + 1
        context = {
            "should_rest": should_rest,
            "can_continue": can_continue,
            "rest_time": rest_time
        }
        return render(request, self.template_name, context)