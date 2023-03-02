from django import template

from ..utils import get_num_user_gold_task, get_user_num_task, get_user_per_gold_task

register = template.Library()


@register.filter(name="get_user_num_task")
def get_user_num_tasks(user):
    return get_user_num_task(user)


@register.filter(name="get_total_gold_tasks")
def get_num_gold_tasks(user):
    return get_num_user_gold_task(user)


@register.filter(name="percentage_gold_task")
def percentage_gold_task(user):
    return get_user_per_gold_task(user)
