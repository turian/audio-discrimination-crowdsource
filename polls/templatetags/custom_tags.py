from django import template

from ..utils import get_user_num_task

register = template.Library()


@register.filter(name="get_user_num_task")
def get_user_num_tasks(user):
    return get_user_num_task(user)
