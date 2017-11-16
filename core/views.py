from .models import Task, Comment
from django.contrib.auth.models import User
from .serializer import UserSerializer, TaskSerializer, CommentSerializer
from rest_framework import viewsets, permissions
from .permissions import IsCreatorOrReadOnly, IsTargetOrReadOnly



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsCreatorOrReadOnly,
                          IsTargetOrReadOnly,
                          )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permissions = (permissions.IsAuthenticated, )


