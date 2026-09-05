from django.conf import settings
from django.db import models


class Board(models.Model):  # Representa la tabla Board en la base de datos
    name = models.CharField(
        max_length=255
    )  # Representan la columna name de la tabla Board en la base de datos
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="boards",
    )  # Representa la foreign key user_id de la tabla Board en la base de datos, que hace referencia a la tabla User
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=[
            ("active", "Active"),
            ("archived", "Archived"),
        ],
        default="active",
        max_length=20,
    )

    def __str__(self) -> str:
        return self.name


class BoardMembership(models.Model):
    ROLE_OWNER = "owner"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_MEMBER, "Member"),
    ]

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="board_memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("board", "user")

    def __str__(self) -> str:
        return f"{self.user} - {self.board} ({self.role})"


class BoardStatus(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="statuses")
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default="#000000")

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.board.name} - {self.name}"


class Sprint(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="sprints")
    name = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.board.name} - {self.name}"


class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    sprint = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    status = models.ForeignKey(
        BoardStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_comments",
    )
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Comment by {self.user} on {self.task}"


class IdempotencyKey(models.Model):
    """Dedupes retried create requests from offline mobile clients (outbox pattern)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="idempotency_keys",
    )
    key = models.CharField(max_length=255)
    endpoint = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "key", "endpoint")

    def __str__(self) -> str:
        return f"{self.endpoint}:{self.key} -> {self.object_id}"
