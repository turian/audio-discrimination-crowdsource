from django import template

from ..utils import (
    get_num_user_gold_task,
    get_user_num_tasks,
    get_user_per_gold_task,
    get_user_roi,
)

register = template.Library()


@register.filter(name="get_num_tasks")
def get_num_tasks(user):
    return get_user_num_tasks(user)


@register.filter(name="get_total_gold_tasks")
def get_num_gold_tasks(user):
    return get_num_user_gold_task(user)


@register.filter(name="percentage_gold_task")
def percentage_gold_task(user):
    return get_user_per_gold_task(user)


@register.filter(name="calculate_roi")
def claculate_roi(user):
    return get_user_roi(user)
