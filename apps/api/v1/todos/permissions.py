from rest_framework import permissions

from apps.todos.models import Board, BoardMembership


def _resolve_board(obj) -> Board:
    if isinstance(obj, Board):
        return obj
    if hasattr(obj, "board_id"):
        return obj.board
    if hasattr(obj, "task_id"):
        return obj.task.board
    raise ValueError(f"Cannot resolve a board for {obj!r}")


class IsBoardMember(permissions.BasePermission):
    """Any member (owner or member) of the object's board."""

    def has_object_permission(self, request, view, obj) -> bool:
        board = _resolve_board(obj)
        return BoardMembership.objects.filter(board=board, user=request.user).exists()


class IsBoardOwnerForUnsafeMethods(permissions.BasePermission):
    """Any member may read; only the board owner may write."""

    def has_object_permission(self, request, view, obj) -> bool:
        board = _resolve_board(obj)
        if request.method in permissions.SAFE_METHODS:
            return BoardMembership.objects.filter(
                board=board, user=request.user
            ).exists()
        return BoardMembership.objects.filter(
            board=board, user=request.user, role=BoardMembership.ROLE_OWNER
        ).exists()


class IsCommentAuthorOrBoardOwnerForUnsafeMethods(permissions.BasePermission):
    """Any board member may read a comment; only its author or the board owner may write to it."""

    def has_object_permission(self, request, view, obj) -> bool:
        board = obj.task.board
        if request.method in permissions.SAFE_METHODS:
            return BoardMembership.objects.filter(
                board=board, user=request.user
            ).exists()
        if obj.user_id == request.user.id:
            return True
        return BoardMembership.objects.filter(
            board=board, user=request.user, role=BoardMembership.ROLE_OWNER
        ).exists()


def boards_for_user(user):
    """Boards the user can access: owned or shared via BoardMembership."""
    return Board.objects.filter(memberships__user=user).distinct()
