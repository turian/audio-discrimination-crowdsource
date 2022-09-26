from rest_framework.serializers import ModelSerializer
from .models import Annotation, Batch, Task


class AnnotationSerializer(ModelSerializer):
    class Meta:
        model = Annotation
        fields = "__all__"


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        exclude = ["batch"]
