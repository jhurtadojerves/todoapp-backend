from django.contrib import admin

from apps.todos.models import (
    Board,
    BoardMembership,
    BoardStatus,
    Comment,
    IdempotencyKey,
    Sprint,
    Task,
)

admin.site.register(Board)
admin.site.register(BoardMembership)
admin.site.register(BoardStatus)
admin.site.register(Sprint)
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(IdempotencyKey)
