from timesheet.models import Stamp, AdditionalRate, PayCheck
from userprofile.models import Contract
from departments.models import Department
from django.contrib.auth.models import User, Group


def create_user(groups=[], departments=[], *args, **kwargs):
    try:
        u = User.objects.create(**kwargs)
    except Exception as e:
        return None
    u.set_password(kwargs["password"])
    if groups == "__all__":
        u.groups.set(Group.objects.all())
    else:
        u.groups.set(Group.objects.filter(name__in=groups))
    u.save()

    if departments == "__all__":
        department_objs = Department.objects.all()
    else:
        department_objs = Department.objects.filter(name__in=departments)

    for department in department_objs:
        department.users.add(u)

    Stamp.objects.create(
        worker=u,
        additonal_rate=AdditionalRate.objects.all()[:1].get()
    )
    PayCheck.objects.create(
        worker=u
    )

    Contract.objects.create(
        worker=u
    )
    u.save()
    return u
