from apps.todos.models import Comment


class CommentService:
    @classmethod
    def create(cls, user, task, content: str) -> Comment:
        return Comment.objects.create(user=user, task=task, content=content)
