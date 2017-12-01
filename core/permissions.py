from rest_framework import permissions


class IsCreatorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.creator == request.user


class IsTargetOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.target == request.user

class IsInTeamToView(permissions.BasePermission):

    def has_view_permission(self, request, view, obj):
        users = obj.members.all()
        if request.user in users:
            return True


