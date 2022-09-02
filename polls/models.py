from django.db import models
from django.contrib.auth import get_user_model

class Batch(models.Model):
    created_at = models.DateTimeField()
    is_gold = models.BooleanField(default=False)
    notes = models.TextField()


class CurrentBatch(models.Model):
    current_batch_gold = models.ForeignKey(Batch, on_delete=models.CASCADE)
    current_batch_eval = models.ForeignKey(Batch, on_delete=models.CASCADE)

class Task(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    reference = models.URLField()
    transform = models.JSONField()

class Annotation(models.Model):
    task_presentation_options = (
        ("AAB", "AAB"),
        ("ABA", "ABA"),
        ("BBA", "BBA"),
        ("BAB", "BAB")
    )
    annotation_options = (
        ("XXY", "XXY"),
        ("XYX", "XYX")
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    annotated_at = models.DateTimeField()

