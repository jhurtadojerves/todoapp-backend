from django.urls import path

from apps.api.v1.todos.views import (
    BoardDetailView,
    BoardListCreateView,
    BoardMembershipDetailView,
    BoardMembershipListCreateView,
    CommentDetailView,
    CommentListCreateView,
    SprintDetailView,
    SprintListCreateView,
    StatusDetailView,
    StatusListCreateView,
    TaskDetailView,
    TaskListCreateView,
)

urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board_list_create"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board_detail"),
    path(
        "boards/<int:board_id>/members/",
        BoardMembershipListCreateView.as_view(),
        name="board_membership_list_create",
    ),
    path(
        "boards/<int:board_id>/members/<int:pk>/",
        BoardMembershipDetailView.as_view(),
        name="board_membership_detail",
    ),
    path(
        "boards/<int:board_id>/statuses/",
        StatusListCreateView.as_view(),
        name="status_list_create",
    ),
    path(
        "boards/<int:board_id>/statuses/<int:pk>/",
        StatusDetailView.as_view(),
        name="status_detail",
    ),
    path(
        "boards/<int:board_id>/sprints/",
        SprintListCreateView.as_view(),
        name="sprint_list_create",
    ),
    path(
        "boards/<int:board_id>/sprints/<int:pk>/",
        SprintDetailView.as_view(),
        name="sprint_detail",
    ),
    path(
        "boards/<int:board_id>/tasks/",
        TaskListCreateView.as_view(),
        name="task_list_create",
    ),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path(
        "tasks/<int:task_id>/comments/",
        CommentListCreateView.as_view(),
        name="comment_list_create",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:pk>/",
        CommentDetailView.as_view(),
        name="comment_detail",
    ),
]
