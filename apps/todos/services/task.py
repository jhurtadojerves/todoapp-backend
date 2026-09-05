from apps.todos.models import Task


class TaskService:
    @classmethod
    def create(cls, user, board, **kwargs) -> Task:
        return Task.objects.create(user=user, board=board, **kwargs)
