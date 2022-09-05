from django.contrib import admin
from .models import Batch, CurrentBatchGold, CurrentBatchEval, Task, Annotation, User

admin.site.register(Batch)
admin.site.register(Task)
admin.site.register(Annotation)
admin.site.register(User)
admin.site.register(CurrentBatchGold)
admin.site.register(CurrentBatchEval)
