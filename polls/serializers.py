from rest_framework import serializers
from .models import Annotation, Batch, Task, CurrentBatchEval, CurrentBatchGold


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["batch"]


class BatchTaskSerializer(serializers.ModelSerializer):
    set_to_current_batch_gold = serializers.BooleanField(default=False)
    set_to_current_batch_eval = serializers.BooleanField(default=False)
    tasks = TaskSerializer(many=True, write_only=True)

    class Meta:
        model = Batch
        fields = "__all__"

    def create(self, validated_data):
        tasks = validated_data.pop("tasks", [])
        set_to_current_batch_gold = validated_data.pop("set_to_current_batch_gold")
        set_to_current_batch_eval = validated_data.pop("set_to_current_batch_eval")
        batch = Batch.objects.create(**validated_data)

        for task_dict in tasks:
            task_dict["batch"] = batch
            Task.objects.create(**task_dict)

        # set to current_batch_gold or current_batch_eval
        if set_to_current_batch_gold and batch.is_gold:
            current_batch_gold = CurrentBatchGold(current_batch_gold=batch)
            current_batch_gold.save()
        elif set_to_current_batch_eval and not batch.is_gold:
            current_batch_eval = CurrentBatchEval(current_batch_eval=batch)
            current_batch_eval.save()

        return batch
