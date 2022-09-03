from django.contrib import admin
from .models import Batch, CurrentBatch, Task, Annotation, User

admin.site.register(Batch)
admin.site.register(CurrentBatch)
admin.site.register(Task)
admin.site.register(Annotation)
admin.site.register(User)
