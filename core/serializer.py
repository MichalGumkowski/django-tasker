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


