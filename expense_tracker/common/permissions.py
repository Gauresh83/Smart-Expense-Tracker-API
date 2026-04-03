from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Object-level permission: only the owner of the object may access or modify it.
    Assumes the model instance has a `user` attribute.
    """
    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(BasePermission):
    """
    Allow read-only access to any authenticated user,
    but write access only to the object's owner.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
