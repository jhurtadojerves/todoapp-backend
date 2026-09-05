from django.db import migrations


def create_owner_memberships(apps, schema_editor):
    Board = apps.get_model("todos", "Board")
    BoardMembership = apps.get_model("todos", "BoardMembership")

    memberships = [
        BoardMembership(board=board, user_id=board.user_id, role="owner")
        for board in Board.objects.all()
    ]
    BoardMembership.objects.bulk_create(memberships, ignore_conflicts=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("todos", "0004_boardmembership_idempotencykey"),
    ]

    operations = [
        migrations.RunPython(create_owner_memberships, noop),
    ]
