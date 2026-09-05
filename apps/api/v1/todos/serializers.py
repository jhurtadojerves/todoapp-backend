from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.todos.dtos.board import BoardData, BoardStatusData, SprintData
from apps.todos.models import Board, BoardMembership, BoardStatus, Comment, Sprint, Task
from apps.todos.services.board import (
    BoardMembershipService,
    BoardService,
    BoardStatusService,
    SprintService,
)
from apps.todos.services.comment import CommentService
from apps.todos.services.task import TaskService

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Board
        fields = ["id", "name", "description", "user_id", "created", "modified"]
        read_only_fields = ["id", "user_id", "created", "modified"]

    def create(self, validated_data):
        data = BoardData(**validated_data)
        return BoardService.create(user=self.context["request"].user, data=data)


class BoardStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardStatus
        fields = ["id", "name", "order", "color"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        board = self.context["board"]
        data = BoardStatusData(**validated_data)
        return BoardStatusService.create(board=board, data=data)


class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ["id", "name", "start_date", "end_date", "created", "modified"]
        read_only_fields = ["id", "created", "modified"]

    def create(self, validated_data):
        board = self.context["board"]
        data = SprintData(**validated_data)
        return SprintService.create(board=board, data=data)


class _StatusBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardStatus
        fields = ["id", "name", "color"]


class _SprintBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    board_id = serializers.IntegerField(read_only=True)

    # Nested read-only representations
    status = _StatusBriefSerializer(read_only=True)
    sprint = _SprintBriefSerializer(read_only=True)

    # Write-only FK fields
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=BoardStatus.objects.all(),
        source="status",
        required=False,
        allow_null=True,
        write_only=True,
    )
    sprint_id = serializers.PrimaryKeyRelatedField(
        queryset=Sprint.objects.all(),
        source="sprint",
        required=False,
        allow_null=True,
        write_only=True,
    )

    # Bidirectional FK (shows pk on read, accepts pk on write)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assigned_to",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "board_id",
            "sprint",
            "sprint_id",
            "status",
            "status_id",
            "user_id",
            "assigned_to_id",
            "title",
            "description",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "board_id", "user_id", "created", "modified"]

    def _get_board(self):
        return self.context.get("board") or (
            self.instance.board if self.instance else None
        )

    def validate(self, attrs):
        board = self._get_board()
        sprint = attrs.get("sprint")
        status = attrs.get("status")
        assigned_to = attrs.get("assigned_to")
        if sprint and sprint.board_id != board.id:
            raise serializers.ValidationError(
                {"sprint_id": "Sprint does not belong to this board."}
            )
        if status and status.board_id != board.id:
            raise serializers.ValidationError(
                {"status_id": "Status does not belong to this board."}
            )
        if (
            assigned_to
            and not BoardMembership.objects.filter(
                board=board, user=assigned_to
            ).exists()
        ):
            raise serializers.ValidationError(
                {"assigned_to_id": "User is not a member of this board."}
            )
        return attrs

    def create(self, validated_data):
        board = self.context["board"]
        return TaskService.create(
            user=self.context["request"].user, board=board, **validated_data
        )


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    task_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "task_id", "user_id", "content", "created", "modified"]
        read_only_fields = ["id", "task_id", "user_id", "created", "modified"]

    def create(self, validated_data):
        task = self.context["task"]
        return CommentService.create(
            user=self.context["request"].user,
            task=task,
            content=validated_data["content"],
        )


class _UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class BoardMembershipSerializer(serializers.ModelSerializer):
    board_id = serializers.IntegerField(read_only=True)
    user = _UserBriefSerializer(read_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = BoardMembership
        fields = ["id", "board_id", "user", "email", "role", "created"]
        read_only_fields = ["id", "board_id", "user", "created"]
        extra_kwargs = {"role": {"required": False}}

    def validate_role(self, value):
        if value == BoardMembership.ROLE_OWNER:
            raise serializers.ValidationError("Cannot assign the owner role directly.")
        return value

    def create(self, validated_data):
        board = self.context["board"]
        email = validated_data.pop("email")
        role = validated_data.get("role", BoardMembership.ROLE_MEMBER)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No user found with this email."}
            )
        return BoardMembershipService.add(board=board, user=user, role=role)
