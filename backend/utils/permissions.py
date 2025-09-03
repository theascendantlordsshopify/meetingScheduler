from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOrganizerOrInvitee(permissions.BasePermission):
    """
    Custom permission for meeting access - organizer or invitee can access.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is the organizer
        if hasattr(obj, 'organizer') and obj.organizer == request.user:
            return True
        
        # Check if user is the invitee (by email)
        if hasattr(obj, 'invitee_email') and obj.invitee_email == request.user.email:
            return True
        
        return False