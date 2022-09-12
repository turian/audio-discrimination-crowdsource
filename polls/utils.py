import random

def batch_selector():
    random.seed()
    return random.random() < 0.9

def present_task_for_user(task):
    """mock function"""
    return "www.example.com", "AAB"