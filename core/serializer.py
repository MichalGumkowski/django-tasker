from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Comment


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'created_tasks', 'assigned_tasks')


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('creator', 'task', 'date', 'text')


class TaskSerializer(serializers.ModelSerializer):

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ('creator', 'target', 'title', 'description', 'created',
                  'deadline', 'priority', 'progress', 'is_finished', 'comments')

    def update(self, instance, validated_data):
        if self.context['request'].user == self.target:
            setattr(instance, 'progress', validated_data.get('progress', None))
            setattr(instance, 'is_finished', validated_data.get('is_finished', None))
            instance.save()
            return instance

        return super(TaskSerializer, self).update(instance, validated_data)