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


class BatchTaskSerializer(ModelSerializer):
    tasks = TaskSerializer(many=True, write_only=True)

    class Meta:
        model = Batch
        fields = "__all__"

    def create(self, validated_data):
        tasks = validated_data.pop("tasks", [])
        batch = Batch.objects.create(**validated_data)

        for task_dict in tasks:
            task_dict["batch"] = batch
            Task.objects.create(**task_dict)
        return batch
