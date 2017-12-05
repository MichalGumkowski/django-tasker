from .models import Task, Comment, Notification, Team, Mail
from .serializer import UserSerializer, TaskSerializer, CommentSerializer, MailSerializer, NotificationSerializer, TeamSerializer
from .permissions import IsCreatorOrReadOnly, IsTargetOrReadOnly, IsInTeamToView

from django.contrib.auth.models import User

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

#           PERMISSIONS!

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @detail_route(methods=['get'], url_path='tasks')
    def tasks(self, request, pk):
        tasks = Task.objects.filter(target_id=pk)
        serializer = TaskSerializer(tasks, many=True,
                                    context={'Request': Request(request)})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='teams')
    def teams(self, request, pk):
        user = self.get_object()

        teams = user.teams.all()

        serializer = TeamSerializer(teams, many=True,
                                    context={'Request': Request(request)})

        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = ()

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

    @detail_route(methods=['get'], url_path='comments')
    def comments(self, request, pk):

        comments = Comment.objects.filter(task__pk=pk)

        serializer = CommentSerializer(comments, many=True,
                                       context={'request': Request(request)})

        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permissions = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission = (permissions.IsAuthenticated, )

    @detail_route(methods=['get'], url_path='users')
    def members(self, request, pk):

        users = User.objects.filter(teams__pk=pk)

        serializer = UserSerializer(users, many=True,
                                    context={'request': Request(request)})

        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='tasks')
    def tasks(self, request, pk):

        tasks = Task.objects.filter(team__pk=pk)

        serializer = TaskSerializer(tasks, many=True,
                                    context={'request': Request(request)})

        return Response(serializer.data)


class MailViewSet(viewsets.ModelViewSet):
    queryset = Mail.objects.all()
    serializer_class = MailSerializer
    permissions = (permissions.IsAdminUser, )


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
