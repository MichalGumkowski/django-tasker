from .models import Task, Comment, Notification, Team, Mail
from .serializer import UserSerializer, TaskSerializer, CommentSerializer, MailSerializer, NotificationSerializer, \
    TeamSerializer
from .permissions import (UserIsTasksTarget,
                          IsInTeamToViewTasksOrMembers,
                          IsInTeamToViewTaskComments,
                          TaskViewSetPermission,
                          NotificationViewSetPermission)

from django.contrib.auth.models import User
from django.http import Http404

from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, permission_classes
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Shows everything related to user's tasks
    @detail_route(methods=['get'], url_path='tasks',
                  permission_classes=(UserIsTasksTarget,))
    def task_list(self, request, pk):
        tasks = Task.objects.filter(target_id=pk)
        serializer = TaskSerializer(tasks, many=True,
                                    context={'Request': Request(request)})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='tasks/(?P<number>[0-9]+)',
                  url_name='user_task',
                  permission_classes=(UserIsTasksTarget,))
    def task_detail(self, request, pk, number):
        try:
            task = Task.objects.filter(id=number)[0]
            serializer = TaskSerializer(task,
                                        context={'request': request})
            return Response(serializer.data)
        except IndexError:
            raise Http404

    @detail_route(methods=['get'], url_path='tasks/(?P<number>[0-9]+)/comments',
                  permission_classes=(UserIsTasksTarget,))
    def task_comments(self, request, pk, number):
        try:
            task = Task.objects.filter(id=number)[0]
            comments = task.comments.all()
            serializer = CommentSerializer(comments,
                                           many=True,
                                           context={'request': request})
            return Response(serializer.data)
        except IndexError:
            raise Http404

    # Shows everything related to user's notifications
    @detail_route(methods=['get'], url_path='notifications',
                  permission_classes=(UserIsTasksTarget,))
    def notification_list(self, request, pk):
        notifications = Notification.objects.filter(target_id=pk)
        serializer = NotificationSerializer(notifications,
                                            many=True,
                                            context={'request': request})
        return Response(serializer.data)

    # Shows everything related to user's teams
    @detail_route(methods=['get'], url_path='teams',
                  permission_classes=(UserIsTasksTarget,))
    def teams(self, request, pk):
        user = self.get_object()
        teams = user.teams.all()
        serializer = TeamSerializer(teams, many=True,
                                    context={'Request': Request(request)})
        return Response(serializer.data)

@permission_classes((TaskViewSetPermission,))
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.pk:
            queryset = user.assigned_tasks.all()
            return queryset
        else:
            raise PermissionDenied({"detail":
                                        "Authentication credentials were not provided."})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        creator = request.user
        possible_teams = creator.teams.all()
        selected_team_pk = request.data['team']
        selected_team = Team.objects.filter(pk=selected_team_pk).first()

        if selected_team in possible_teams:
            target_pk = request.data['target']
            target = User.objects.filter(pk=target_pk).first()
            if target in selected_team.members.all():
                self.perform_create(serializer)
            else:
                raise ValidationError('There is no user named {} in '
                                      'your team'.format(target.username))
        else:
            raise ValidationError('You don\'t have a permission to add '
                                  'anyone to {}'.format(selected_team))

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @detail_route(methods=['get'], url_path='comments',
                  permission_classes=(IsInTeamToViewTaskComments,))
    def comments(self, request, pk):

        comments = Comment.objects.filter(task__pk=pk)

        serializer = CommentSerializer(comments, many=True,
                                       context={'request': Request(request)})

        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


#dorobić permission
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    @detail_route(methods=['get'], url_path='users',
                  permission_classes=(IsInTeamToViewTasksOrMembers,))
    def members(self, request, pk):
        users = User.objects.filter(teams__pk=pk)
        serializer = UserSerializer(users, many=True,
                                    context={'request': Request(request)})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='tasks',
                  permission_classes=(IsInTeamToViewTasksOrMembers,))
    def task_list(self, request, pk):
        tasks = Task.objects.filter(team__pk=pk)
        serializer = TaskSerializer(tasks, many=True,
                                    context={'request': Request(request)})
        return Response(serializer.data)

    # dorobić permissions
    @detail_route(methods=['get'], url_path='tasks/(?P<number>[0-9]+)',
                  permission_classes=(IsInTeamToViewTasksOrMembers,))
    def task_detail(self, request, pk, number):
        task = Task.objects.filter(id=number)[0]
        serializer = TaskSerializer(task,
                                    context={'request': request})
        return Response(serializer.data)

    # dorobić permissions
    @detail_route(methods=['get'], url_path='tasks/(?P<number>[0-9]+)/comments',
                  permission_classes=(IsInTeamToViewTasksOrMembers,))
    def task_comments(self, request, pk, number):
        try:
            task = Task.objects.filter(id=number)[0]
            comments = task.comments.all()
            serializer = CommentSerializer(comments,
                                           many=True,
                                           context={'request': request})
            return Response(serializer.data)
        except IndexError:
            raise Http404


@permission_classes((IsAdminUser,))
class MailViewSet(viewsets.ModelViewSet):
    queryset = Mail.objects.all()
    serializer_class = MailSerializer


@permission_classes((NotificationViewSetPermission, ))
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.pk:
            queryset = user.notification.all()
            return queryset
        else:
            PermissionDenied({"detail":
                                  "Authentication credentials were not provided."})


