import random

from django.utils import timezone

from .models import (
    Annotation,
    ExperimentTypeAnnotation,
    ExperimentTypeTaskPresentation,
    Task,
)

random.seed()


def batch_selector():
    return random.random() < 0.9


def present_task_for_user(task):
    """mock function"""
    audios = [task.reference_url, task.transform_url]
    experiment_type = task.batch.experiment_type
    task_presentations = ExperimentTypeTaskPresentation.objects.filter(
        experiment_type=experiment_type
    )
    task_presentation_chosen = random.choice(task_presentations).task_presentation
    unique_chars = set(task_presentation_chosen)
    audio_mapping = {}
    for index, key in enumerate(unique_chars):
        audio_mapping[key] = audios[index]
    return audio_mapping, task_presentation_chosen


def check_user_work_permission(user):
    """Implements User Auth Flow
    Checks if user can work or rest and calclulates resting time
    """
    minutes_after_should_rest = 15
    minutes_after_can_continue = 75
    current_time = timezone.now()
    if not user.first_task_of_this_session_performed_at:
        return True, False, 0
    time_diff = current_time - user.first_task_of_this_session_performed_at
    time_diff_minutes = time_diff.total_seconds() / 60
    should_rest = (
        time_diff_minutes > minutes_after_should_rest
        and time_diff_minutes < minutes_after_can_continue
    )
    can_continue = time_diff_minutes > minutes_after_can_continue
    rest_time = round(minutes_after_can_continue - time_diff_minutes)
    return can_continue, should_rest, rest_time


def get_user_num_tasks(user):
    """Generate number of task a user completed then return
    the value to be used in template tags
    """
    task_count = Annotation.objects.filter(user=user).count()

    return task_count


def get_num_user_gold_task(user):
    """Generate the number of gold tasks a user completed then return
    it's value for use in template tags
    """
    gold_count = Annotation.objects.filter(user=user, task__batch__is_gold=True).count()

    return gold_count


def get_user_per_gold_task(user):
    """Generate the percentage of Gold task a user completed
    by annotating throuh total task
    """

    total_task = get_user_num_tasks(user)
    gold_task = get_num_user_gold_task(user)
    if total_task == 0:
        return 0
    percentage_gold = float(gold_task / total_task) * 100

    return percentage_gold


def get_user_roi(user):
    """ """
    pass


def parse_data_for_admin_experiment(batches):
    data_list = []
    for batch in batches:
        tasks = Task.objects.filter(batch=batch)
        data_dict = {"batch": batch.id, "tasks": tasks, "is_gold": batch.is_gold}
        data_list.append(data_dict)
    return data_list


def create_audio_list(audios, task_presentation):
    audio_list = []
    for char in task_presentation:
        audio_list.append(audios[char])

    return audio_list


def get_task_annotations(experiment_type):
    task_annotations = ExperimentTypeAnnotation.objects.filter(
        experiment_type=experiment_type
    )
    return task_annotations
