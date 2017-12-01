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
        fields = ('creator', 'team', 'target', 'title', 'description', 'created',
                  'deadline', 'priority', 'progress', 'is_finished', 'comments')

    def create(self, validated_data):
        creator = self.context['request'].user
        possible_teams = creator.team.all()
        selected_team = validated_data.get('team')
        if selected_team in possible_teams:
            target = validated_data.get('target')
            if target in selected_team.members.all():
                return super(TaskSerializer, self).create(validated_data)
            else:
                raise ValueError('The person you assigned your task '
                                 'to is not in selected team!')

        else:
            raise ValueError('You cannot add a task to a team you '
                             'do not belong to')

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
