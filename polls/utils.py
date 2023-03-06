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
    """
    This function takes task as argument, chooses a random task
    presentation and maps the audios with every unique character
    of task presentation string
    """
    audios_list = [task.reference_url, task.transform_url]
    experiment_type = task.batch.experiment.experiment_type
    task_presentation = get_random_task_presentation(experiment_type)

    # to get unique characters from task_presentations for dict mapping
    presentation_set = set(task_presentation)

    audio_mapping = map_audios_to_dict(presentation_set, audios_list)
    return audio_mapping, task_presentation


def get_random_task_presentation(experiment_type):
    """
    This function takes 'experiment_type' as argument and returns
    a task_presentation chosen randomly to show to user
    """
    task_presentations = ExperimentTypeTaskPresentation.objects.filter(
        experiment_type=experiment_type
    )
    random_task_presentation = random.choice(task_presentations).task_presentation
    return random_task_presentation


def map_audios_to_dict(presentation_set, audios_list):
    """
    This function takes 'presentation_set' and 'audios_list' as arguments
    and maps the audios in 'audios_list' to every character in 'presentation_set'
    """
    audio_mapping = {}
    for item in audios_list:
        audio_mapping[presentation_set.pop()] = item
    return audio_mapping


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
    """
    This function takes 'audios' and 'task_presentation' as arguments
    and creates a list of audios and returns it
    """
    audio_list = []
    for char in task_presentation:
        audio_list.append(audios[char])

    return audio_list


def get_task_annotations(experiment_type):
    """
    This function takes 'experiment_type' as argument
    and returns task_annotations for it
    """
    task_annotations = ExperimentTypeAnnotation.objects.filter(
        experiment_type=experiment_type
    )
    return task_annotations
