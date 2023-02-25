from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class User(AbstractUser):
    first_task_of_this_session_performed_at = models.DateTimeField(null=True)
    is_locked = models.BooleanField(default=False)


class Batch(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_gold = models.BooleanField(default=False)
    notes = models.TextField()

    class Meta:
        verbose_name_plural = "batches"


class CurrentBatchGold(SingletonModel):
    current_batch_gold = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="current_batch_gold",
        limit_choices_to={"is_gold": True},
        blank=True,
        null=True,
    )


class CurrentBatchEval(SingletonModel):
    current_batch_eval = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="current_batch_eval",
        limit_choices_to={"is_gold": False},
        blank=True,
        null=True,
    )


class Task(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="tasks")
    reference_url = models.URLField()
    transform_url = models.URLField()
    transform_metadata = models.JSONField()


class Annotation(models.Model):
    TASK_PRESENTATION_OPTIONS = (
        ("AAB", "AAB"),
        ("ABA", "ABA"),
        ("BBA", "BBA"),
        ("BAB", "BAB"),
    )
    ANNOTATION_OPTIONS = (("XXY", "XXY"), ("XYX", "XYX"))
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="annotations"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    annotated_at = models.DateTimeField()
    task_presentation = models.CharField(
        max_length=3, choices=TASK_PRESENTATION_OPTIONS
    )
    annotations = models.CharField(max_length=3, choices=ANNOTATION_OPTIONS)

    def __str__(self):
        return f"Annotation by {self.user.username}"


class ExperimentType(models.Model):
    type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type}"


class Experiment(models.Model):
    name = models.CharField(max_length=100)
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.CASCADE)
    task_presentation = ArrayField(models.CharField(max_length=100), default=list)
    annotation = ArrayField(models.CharField(max_length=100), default=list)

    def __str__(self):
        return f"{self.name}"
