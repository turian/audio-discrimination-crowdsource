from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class ExperimentType(models.Model):
    type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.type}"


class Experiment(models.Model):
    name = models.CharField(max_length=150, unique=True)
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class Batch(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_gold = models.BooleanField(default=False)
    notes = models.TextField()
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="batches",
        null=True,
        blank=True,
    )

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
    transform_metadata = models.JSONField(blank=True, null=True)


class AnnotatorProfile(models.Model):
    annotator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user"
    )
    email = models.EmailField(blank=True)
    hourly_rate = models.FloatField(default=None, editable=True, blank=True, null=True)

    def __str__(self):
        return self.email


class Annotation(models.Model):
    TASK_PRESENTATION_OPTIONS = (
        ("AAB", "AAB"),
        ("ABA", "ABA"),
        ("BBA", "BBA"),
        ("BAB", "BAB"),
    )
    ANNOTATION_OPTIONS = (("XXY", "XXY"), ("XYX", "XYX"))
    user = models.ForeignKey(
        AnnotatorProfile, on_delete=models.CASCADE, related_name="annotations"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="annotation")
    annotated_at = models.DateTimeField()
    task_presentation = models.CharField(
        max_length=3, choices=TASK_PRESENTATION_OPTIONS
    )
    annotations = models.CharField(max_length=3, choices=ANNOTATION_OPTIONS)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Annotation by {self.user}"


class ExperimentTypeTaskPresentation(models.Model):
    task_presentation = models.CharField(max_length=100)
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.task_presentation}"


class ExperimentTypeAnnotation(models.Model):
    annotation = models.CharField(max_length=100)
    experiment_type = models.ForeignKey(ExperimentType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.annotation}"


CustomUser = get_user_model()


@receiver(post_save, sender=CustomUser)
def update_user_profile(sender, instance, created, **kwargs):
    """
    Signals the Profile about temp User creation.
    """
    if created:
        profile = AnnotatorProfile.objects.create(annotator=instance)
        profile.save()


@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    profile = AnnotatorProfile.objects.create(annotator=instance)
    profile.save()
