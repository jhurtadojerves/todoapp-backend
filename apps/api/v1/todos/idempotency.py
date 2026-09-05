from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.todos.models import IdempotencyKey

IDEMPOTENCY_HEADER = "Idempotency-Key"


class IdempotentCreateMixin:
    """Dedupes retried POSTs (mobile offline outbox pattern) via an Idempotency-Key header.

    Subclasses must set `idempotency_model` to the model created by this view.
    """

    idempotency_model = None

    def create(self, request, *args, **kwargs):
        key = request.headers.get(IDEMPOTENCY_HEADER)
        if not key:
            return super().create(request, *args, **kwargs)

        endpoint = self.__class__.__name__
        existing = IdempotencyKey.objects.filter(
            user=request.user, key=key, endpoint=endpoint
        ).first()
        if existing:
            obj = get_object_or_404(self.idempotency_model, pk=existing.object_id)
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
