from django.contrib import admin

from .models import (
    Annotation,
    Batch,
    CurrentBatchEval,
    CurrentBatchGold,
    Experiment,
    ExperimentType,
    AnnotatorProfile,
    Task,
    User,
)

admin.site.register(Batch)
admin.site.register(Task)
admin.site.register(Annotation)
admin.site.register(User)
admin.site.register(CurrentBatchGold)
admin.site.register(CurrentBatchEval)
admin.site.register(Experiment)
admin.site.register(ExperimentType)
admin.site.register(AnnotatorProfile)

