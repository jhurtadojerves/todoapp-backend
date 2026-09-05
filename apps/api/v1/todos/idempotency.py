from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.todos.models import IdempotencyKey

IDEMPOTENCY_HEADER = "Idempotency-Key"


class IdempotentCreateMixin:
    """Dedupes retried POSTs (mobile offline outbox pattern) via an Idempotency-Key header."""

    def _idempotency_scope(self) -> str:
        """Scopes the key by view + URL kwargs (board_id/task_id) so the same key
        reused by the same user under a different board/task can't collide."""
        kwargs_scope = ",".join(f"{k}={v}" for k, v in sorted(self.kwargs.items()))
        return f"{self.__class__.__name__}:{kwargs_scope}"

    def create(self, request, *args, **kwargs):
        key = request.headers.get(IDEMPOTENCY_HEADER)
        if not key:
            return super().create(request, *args, **kwargs)

        endpoint = self._idempotency_scope()
        existing = IdempotencyKey.objects.filter(
            user=request.user, key=key, endpoint=endpoint
        ).first()
        if existing:
            # Replay through the view's own (membership-scoped) queryset, never the
            # raw model manager, so a stale/foreign object_id can't leak data the
            # requester no longer has access to.
            obj = get_object_or_404(self.get_queryset(), pk=existing.object_id)
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            IdempotencyKey.objects.create(
                user=request.user,
                key=key,
                endpoint=endpoint,
                object_id=response.data["id"],
            )
        return response
