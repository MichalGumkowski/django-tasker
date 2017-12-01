from .models import Task, Comment, Notification, Team, Mail
from django.contrib.auth.models import User
from .serializer import UserSerializer, TaskSerializer, CommentSerializer, MailSerializer, NotificationSerializer, TeamSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import detail_route, list_route
from rest_framework.request import Request
from rest_framework.response import Response
from .permissions import IsCreatorOrReadOnly, IsTargetOrReadOnly, IsInTeamToView


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['get'], url_path='tasks')
    def tasks(self, request):
        user = self.get_object()
        tasks = Task.objects.filter(user__pk=user.pk)
        serializer = TaskSerializer(tasks, many=True,
                                    context={'Request': Request(request)})
        return serializer


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsCreatorOrReadOnly,
                          IsTargetOrReadOnly,
                          IsInTeamToView,
                          )

    def get_queryset(self):
        return self.request.user.team.all()

    @list_route(methods=['get'], url_path='comments')
    def comments(self, request):

        task = self.get_object()

        comments = Comment.objects.filter(Task__pk=task.pk)

        serializer = CommentSerializer(comments, many=True,
                                       context={'request': Request(request)})

        return Response(serializer)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permissions = (permissions.IsAuthenticated, )


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission = (permissions.IsAuthenticated, )

    @list_route(methods=['get'], url_path='users')
    def members(self, request):
        team = self.get_object()

        members = User.objects.filter(team__pk=team.pk)
        serializer = UserSerializer(members, many=True,
                                    context={'request': Request(request)})

        return Response(serializer)


class MailViewSet(viewsets.ModelViewSet):
    queryset = Mail.objects.all()
    serializer_class = MailSerializer
    permissions = (permissions.IsAdminUser, )


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer



