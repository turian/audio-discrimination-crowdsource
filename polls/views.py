import json
import os

import markdown
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
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
from .models import (
    Annotation,
    AnnotatorProfile,
    Batch,
    CurrentBatchEval,
    CurrentBatchGold,
    Experiment,
    ExperimentType,
    ExperimentTypeAnnotation,
    ExperimentTypeTaskPresentation,
    Task,
)
from .serializers import AnnotationSerializer, BatchTaskSerializer
from .utils import (
    batch_selector,
    check_user_work_permission,
    create_audio_list,
    get_task_annotations,
    parse_data_for_admin_experiment,
    present_task_for_user,
    set_is_correct,
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
        batches = Batch.objects.all()
        context = {
            "experiments": experiments,
            "batches": batches,
        }
        return render(request, self.template_name, context)


class AdminExperimentView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "polls/admin_experiment.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, experiment_id):
        try:
            experiment = Experiment.objects.get(id=experiment_id)
            batches = experiment.batches.all().order_by("-is_gold")
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
            tasks_for_user = current_batch.tasks.exclude(
                annotation__user__annotator=request.user
            )
            task = tasks_for_user.first()
            if task:
                experiment_type = task.batch.experiment.experiment_type
                task_annotations = get_task_annotations(experiment_type)
                audios, task_presentation = present_task_for_user(task)
                audio_list = create_audio_list(audios, task_presentation)

                # set zipped_list(audios, annotations) and reference audio
                # according to experiment_type
                if experiment_type.type == "2AFC":
                    zipped_list = list(zip(audio_list[1:], task_annotations))
                    reference_audio = audio_list[0]
                else:
                    zipped_list = list(zip(audio_list, task_annotations))
                    reference_audio = None

                context = {
                    "task": task,
                    "batch_id": task.batch.id,
                    "task_presentation": task_presentation,
                    "zipped_list": zipped_list,
                    "reference_audio": reference_audio,
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


class CreateAnnotation(CheckUserLockMixin, LoginRequiredMixin, View):
    template_name = "polls/task_flow_form.html"

    def post(self, request):
        annotator = AnnotatorProfile.objects.get(annotator=request.user)
        task_pk = request.POST.get("taskPk")
        annotation_choice = request.POST.get("annotationOption")
        batch_id = request.POST.get("batch_id")
        task_presentation = request.POST.get("taskPresentation")

        if not task_pk:
            return render(request, self.template_name, {})

        task = get_object_or_404(Task, pk=task_pk)

        anotation_obj = Annotation.objects.create(
            user=annotator,
            task=task,
            annotated_at=timezone.now(),
            task_presentation=task_presentation,
            annotations=annotation_choice,
        )

        set_is_correct(anotation_obj)

        current_batch = get_object_or_404(Batch, id=batch_id)
        tasks_for_user = current_batch.tasks.exclude(
            annotation__user__annotator=request.user
        )
        task = tasks_for_user.first()

        context = {}
        if task:
            experiment_type = task.batch.experiment.experiment_type
            task_annotations = get_task_annotations(experiment_type)
            audios, task_presentation = present_task_for_user(task)
            audio_list = create_audio_list(audios, task_presentation)

            # set zipped_list(audios, annotations) and reference audio
            # according to experiment_type
            if experiment_type.type == "2AFC":
                zipped_list = list(zip(audio_list[1:], task_annotations))
                reference_audio = audio_list[0]
            else:
                zipped_list = list(zip(audio_list, task_annotations))
                reference_audio = None

            context = {
                "task": task,
                "batch_id": task.batch.id,
                "task_presentation": task_presentation,
                "zipped_list": zipped_list,
                "reference_audio": reference_audio,
            }
        return render(request, self.template_name, context)


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


class ThanksView(TemplateView):
    template_name = "polls/thanks.html"


class AdminManagementView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        annotators = AnnotatorProfile.objects.all()

        context = {
            "annotators": annotators,
        }
        return render(request, "polls/admin-management.html", context)

    def test_func(self):
        return self.request.user.is_superuser


class LockUserView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, user_id, *args, **kwargs):
        user = get_user_model().objects.get(pk=user_id)
        if user.is_locked:
            user.is_locked = False
            user.save()
            return HttpResponse("Lock")
        else:
            user.is_locked = True
            user.save()
            return HttpResponse("Unlock")

    def test_func(self):
        return self.request.user.is_superuser


class PerformDelete(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(request, user_id, *args, **kwargs):
        user = get_user_model().objects.get(id=user_id)
        annotations = Annotation.objects.filter(user=user)
        for annotation in annotations:
            annotation.delete()
        user.is_locked = True
        user.save()
        return HttpResponse("success")

    def test_func(self):
        return self.request.user.is_superuser


class AdminCreateExperimentTypeView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        return render(request, "polls/experiment-type-form.html")

    def post(self, request, *args, **kwargs):
        new_experiment_type = request.POST.get("experiment-type")
        experiment_types = ExperimentType.objects.all()
        if new_experiment_type in experiment_types:
            return HttpResponse("Experiment Type Already Exist")
        else:
            create_type = ExperimentType.objects.create(
                type=str(new_experiment_type).upper()
            )
            create_type.save()
            return HttpResponse("successfully created new experiment type")

    def test_func(self):
        return self.request.user.is_superuser


class AdminCreateExperimentView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        experiment_type = ExperimentType.objects.all()
        context = {"exp_types": experiment_type}
        return render(request, "polls/create-experiment-form.html", context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("experiment-name")
        type_pk = request.POST.get("experiment-type")
        experiment = Experiment.objects.filter(name=name).exists()
        exp_type = ExperimentType.objects.get(pk=type_pk)
        if experiment:
            return HttpResponse("An experiment with this name already exist")

        if exp_type:
            new_experiment = Experiment.objects.create(
                name=str(name), experiment_type=exp_type
            )
            new_experiment.save()
            return HttpResponse("successfully created")

        else:
            return HttpResponse("Please select experiment type from dropdown")

    def test_func(self):
        return self.request.user.is_superuser


class AdminBatchSubmitView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        experiments = Experiment.objects.all()
        context = {"experiments": experiments}
        return render(request, "polls/admin-batch-submit.html", context)

    def post(self, request, *args, **kwargs):
        json_data = request.POST.get("json-data")
        exp_pk = request.POST.get("exp_pk")
        experiment_id = Experiment.objects.filter(pk=int(exp_pk))
        db_data = json.loads(json_data)
        if experiment_id.exists():
            experiment = Experiment.objects.get(pk=exp_pk)
            new_batch = Batch.objects.create(
                name=db_data["name"] if db_data["name"] else None,
                is_gold=db_data["is_gold"] if db_data["is_gold"] else False,
                notes=db_data["notes"] if db_data["notes"] else "",
                experiment=experiment,
            )
            new_batch.save()
            for task in db_data["tasks"]:
                new_task = Task.objects.create(
                    batch=new_batch,
                    reference_url=task["reference_url"],
                    transform_url=task["transform_url"],
                    transform_metadata=task["transform_metadata"]
                    if task["transform_metadata"]
                    else None,
                )
                new_task.save()
            return HttpResponseRedirect(reverse("admin_dashboard"))
        else:
            return HttpResponse(
                "reference experiment does not exist, please choose from drop-down."
            )

    def test_func(self):
        return self.request.user.is_superuser


class ToggleIsGoldView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, batch_pk, *args, **kwargs):
        batch = get_object_or_404(Batch, pk=batch_pk)
        if batch.is_gold:
            batch.is_gold = False
            batch.save()
            return HttpResponse("False")
        else:
            batch.is_gold = True
            batch.save()
            return HttpResponse("True")

    def test_func(self):
        return self.request.user.is_superuser


class TemporaryLogin(View):
    template_name = "polls/temp_login_result.html"

    def post(self, request):
        context = {"message": "You have been logged in temporarily"}
        query_email = request.POST.get("email", None)
        username = query_email.split("@")[0]
        temp_password = "Asdfghjkl123"
        try:
            temp_user = get_user_model().objects.create_user(
                username=username, email=query_email, password=temp_password
            )
            temp_user.save()
            user = authenticate(request, username=username, password=temp_password)
            login(request, user)
        except IntegrityError:
            context["message"] = "A user with this email already exists"
        return render(request, self.template_name, context)


class TemporaryLoginTemplate(TemplateView):
    template_name = "polls/temp_login_template.html"


class CreateExperimentTypeAnnotationView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        experiment_types = ExperimentType.objects.all()
        context = {"experiment_types": experiment_types}
        return render(request, "polls/experiment-type-annotation.html", context)

    def post(self, request, *args, **kwargs):
        exp_type = request.POST.get("experiment-type")
        annotation = request.POST.get("annotation")
        experiment_type = ExperimentType.objects.filter(pk=exp_type)

        if experiment_type.exists():
            expe_type = ExperimentType.objects.get(pk=exp_type)
            exp_type_annotation = ExperimentTypeAnnotation.objects.create(
                experiment_type=expe_type, annotation=str(annotation)
            )
            exp_type_annotation.save()

            return HttpResponse("Successfully created new experiment type annotation")

        else:
            return HttpResponse("Select experiment type from dropdown")

    def test_func(self):
        return self.request.user.is_superuser


class CreateExperimentTypeTaskPresentationView(
    LoginRequiredMixin, UserPassesTestMixin, View
):
    def get(self, request):
        experiment_types = ExperimentType.objects.all()
        context = {"experiment_types": experiment_types}
        return render(request, "polls/experiment_type_task_presentation.html", context)

    def post(self, request, *args, **kwargs):
        exp_type = request.POST.get("experiment_type")
        task_presentation = request.POST.get("task_presentaion")
        try:
            experiment_type = ExperimentType.objects.get(pk=exp_type)
            exp_type_annotation = ExperimentTypeTaskPresentation.objects.create(
                experiment_type=experiment_type,
                task_presentation=str(task_presentation),
            )
            exp_type_annotation.save()

            return HttpResponse("Successfully added new type task presentation")

        except ExperimentType.DoesNotExist:
            return HttpResponse("Select experiment type from dropdown")

    def test_func(self):
        return self.request.user.is_superuser


class ManageExperimentTypeCreationView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        return render(request, "polls/experiment-type-creation-management.html")

    def test_func(self):
        return self.request.user.is_superuser


class AdminQuickGuideView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        file_path = os.path.join(settings.BASE_DIR, "admin-quickstart.MD")
        with open(file_path, "r") as file:
            content = file.read()
            page_html = markdown.markdown(content)

            return render(
                request, "polls/admin-quickguide.html", {"page_html": page_html}
            )

    def test_func(self):
        return self.request.user.is_superuser


class DisplayAnnotationsView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, annotator_id):
        annotations = Annotation.objects.filter(user=annotator_id)
        context = {
            "annotations": annotations,
        }
        return render(request, "polls/annotations.html", context)

    def test_func(self):
        return self.request.user.is_superuser


# **************** API Views ******************* #
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


class AdminAPIView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        return Response({"data": "hello"}, status.HTTP_200_OK)

    def test_func(self):
        return self.request.user.is_superuser
