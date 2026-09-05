from django.db import transaction

from apps.todos.dtos.board import BoardData, BoardStatusData, SprintData
from apps.todos.models import Board, BoardMembership, BoardStatus, Sprint


class BoardService:
    @classmethod
    def create(cls, user, data: BoardData) -> Board:
        with transaction.atomic():
            board = Board.objects.create(user=user, **data.model_dump())
            BoardMembership.objects.create(
                board=board, user=user, role=BoardMembership.ROLE_OWNER
            )
        return board


class BoardStatusService:
    @classmethod
    def create(cls, board: Board, data: BoardStatusData) -> BoardStatus:
        return BoardStatus.objects.create(board=board, **data.model_dump())


class SprintService:
    @classmethod
    def create(cls, board: Board, data: SprintData) -> Sprint:
        return Sprint.objects.create(board=board, **data.model_dump())


class BoardMembershipService:
    @classmethod
    def add(
        cls, board: Board, user, role: str = BoardMembership.ROLE_MEMBER
    ) -> BoardMembership:
        membership, _ = BoardMembership.objects.get_or_create(
            board=board, user=user, defaults={"role": role}
        )
        return membership

    @classmethod
    def remove(cls, membership: BoardMembership) -> None:
        membership.delete()
