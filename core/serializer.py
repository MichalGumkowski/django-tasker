from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Comment, Notification, Mail, Team, team_changed
from django.contrib.sites.models import Site
import datetime


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'created_tasks', 'assigned_tasks', 'notification')


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


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ('name', 'description', 'members')

    def create(self, validated_data):
        name = validated_data.get('name')

        users = validated_data.get('members')
        not_text = "You have been added do the team <b>" + name + "</b>"

        domain = Site.objects.get_current().domain
        path = "/teams/" + str(Team.objects.count()+1) + "/"
        url = 'http://{domain}{path}'.format(domain=domain, path=path)
        date = datetime.datetime.now()

        for user in users:
            Notification.objects.create(target=user, text=not_text,
                                        date=date, link=url, seen=False)

        return super(TeamSerializer, self).create(validated_data)

    #send notification with previous and actual users in the group
    def update(self, instance, validated_data):
        old_members = []
        for member in instance.members.all():
            old_members.append(member)

        update = super(TeamSerializer, self).update(instance, validated_data)

        team_changed(instance, old_members)

        return update


class MailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mail
        fields = ('target', 'title', 'text', 'sent')


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('target', 'text', 'date', 'link', 'seen')
