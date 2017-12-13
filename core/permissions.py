from rest_framework import permissions


class UserIsTasksTarget(permissions.BasePermission):

    def has_permission(self, request, view):
        obj = view.get_object()
        return request.user == obj


class IsInTeamToViewTasksOrMembers(permissions.BasePermission):

    def has_permission(self, request, view):
        obj = view.get_object()
        members = obj.members.all()
        if request.user in members:
            return True


class IsInTeamToViewTaskComments(permissions.BasePermission):
    def has_permission(self, request, view):
        task = view.get_object()
        team = task.team
        members = team.members.all()
        return request.user in members


class TaskViewSetPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        team = obj.team
        members = team.members.all()
        return request.user in members


class NotificationViewSetPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        target = obj.target
        return request.user == target



