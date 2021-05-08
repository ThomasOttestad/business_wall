from messageboard.models import Board
from .models import Department

def create_department(users=[], **kwargs):
    b = None
    try:
        name = kwargs["name"]
        b = Board.objects.create(name=name, description=f"Messageboard for {name} department.", dep=True)
        d = Department.objects.create(board=b, **kwargs)
    except Exception as e:
        if b:
            b.delete()
        return None
    d.users.add(*users)
    return d
