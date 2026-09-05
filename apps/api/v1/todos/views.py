from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404

from apps.api.v1.todos.idempotency import IdempotentCreateMixin
from apps.api.v1.todos.permissions import (
    IsBoardMember,
    IsBoardOwnerForUnsafeMethods,
    boards_for_user,
)
from apps.api.v1.todos.serializers import (
    BoardMembershipSerializer,
    BoardSerializer,
    BoardStatusSerializer,
    CommentSerializer,
    SprintSerializer,
    TaskSerializer,
)
from apps.todos.models import Board, BoardMembership, BoardStatus, Comment, Sprint, Task


@extend_schema(tags=["v1/boards"])
class BoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Board.objects.none()
        return boards_for_user(self.request.user).order_by("-created")


@extend_schema(tags=["v1/boards"])
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerForUnsafeMethods]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Board.objects.none()
        return boards_for_user(self.request.user)


@extend_schema(tags=["v1/boards"])
class BoardMembershipListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_board(self):
        if getattr(self, "swagger_fake_view", False):
            return Board()
        return get_object_or_404(
            boards_for_user(self.request.user), pk=self.kwargs["board_id"]
        )

    def get_queryset(self):
        return BoardMembership.objects.filter(board=self.get_board()).select_related(
            "user"
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["board"] = self.get_board()
        return ctx

    def perform_create(self, serializer):
        board = self.get_board()
        is_owner = BoardMembership.objects.filter(
            board=board, user=self.request.user, role=BoardMembership.ROLE_OWNER
        ).exists()
        if not is_owner:
            raise PermissionDenied("Only the board owner can add members.")
        serializer.save()


@extend_schema(tags=["v1/boards"])
class BoardMembershipDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = BoardMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "delete"]

    def get_board(self):
        if getattr(self, "swagger_fake_view", False):
            return Board()
        return get_object_or_404(
            boards_for_user(self.request.user), pk=self.kwargs["board_id"]
        )

    def get_queryset(self):
        return BoardMembership.objects.filter(board=self.get_board()).select_related(
            "user"
        )

    def perform_destroy(self, instance):
        is_owner = BoardMembership.objects.filter(
            board=instance.board,
            user=self.request.user,
            role=BoardMembership.ROLE_OWNER,
        ).exists()
        if not is_owner:
            raise PermissionDenied("Only the board owner can remove members.")
        if instance.role == BoardMembership.ROLE_OWNER:
            raise ValidationError("Cannot remove the board owner.")
        instance.delete()


@extend_schema(tags=["v1/boards"])
class StatusListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_board(self):
        if getattr(self, "swagger_fake_view", False):
            return Board()
        return get_object_or_404(
            boards_for_user(self.request.user), pk=self.kwargs["board_id"]
        )

    def get_queryset(self):
        return BoardStatus.objects.filter(board=self.get_board())

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["board"] = self.get_board()
        return ctx


@extend_schema(tags=["v1/boards"])
class StatusDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_board(self):
        if getattr(self, "swagger_fake_view", False):
            return Board()
        return get_object_or_404(
            boards_for_user(self.request.user), pk=self.kwargs["board_id"]
        )

    def get_queryset(self):
        return BoardStatus.objects.filter(board=self.get_board())

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["board"] = self.get_board()
        return ctx


@extend_schema(tags=["v1/boards"])
class SprintListCreateView(generics.ListCreateAPIView):
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_board(self):
        if getattr(self, "swagger_fake_view", False):
            return Board()
        return get_object_or_404(
            boards_for_user(self.request.user), pk=self.kwargs["board_id"]
        )

    def get_queryset(self):
        return Sprint.objects.filter(board=self.get_board())

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["board"] = self.get_board()
        return ctx


@extend_schema(tags=["v1/boards"])
class SprintDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_board(self):
        if getattr(self, "swagger_fake_view", False):
            return Board()
        return get_object_or_404(
            boards_for_user(self.request.user), pk=self.kwargs["board_id"]
        )

    def get_queryset(self):
        return Sprint.objects.filter(board=self.get_board())


@extend_schema(tags=["v1/tasks"])
class TaskListCreateView(IdempotentCreateMixin, generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "sprint", "assigned_to"]
    idempotency_model = Task

    def get_board(self):
        if getattr(self, "swagger_fake_view", False):
            return Board()
        return get_object_or_404(
            boards_for_user(self.request.user), pk=self.kwargs["board_id"]
        )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()
        return (
            Task.objects.filter(board=self.get_board())
            .select_related("status", "sprint", "user", "assigned_to")
            .order_by("-created")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["board"] = self.get_board()
        return ctx


@extend_schema(tags=["v1/tasks"])
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardMember]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()
        return (
            Task.objects.filter(board__memberships__user=self.request.user)
            .select_related("board", "status", "sprint", "user", "assigned_to")
            .distinct()
        )


@extend_schema(tags=["v1/tasks"])
class CommentListCreateView(IdempotentCreateMixin, generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    idempotency_model = Comment

    def get_task(self):
        if getattr(self, "swagger_fake_view", False):
            return Task()
        return get_object_or_404(
            Task.objects.filter(board__memberships__user=self.request.user).distinct(),
            pk=self.kwargs["task_id"],
        )

    def get_queryset(self):
        return (
            Comment.objects.filter(task=self.get_task())
            .select_related("user")
            .order_by("created")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["task"] = self.get_task()
        return ctx


@extend_schema(tags=["v1/tasks"])
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Comment.objects.none()
        return Comment.objects.filter(
            task_id=self.kwargs["task_id"],
            task__board__memberships__user=self.request.user,
        ).select_related("user")
