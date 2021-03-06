# Generated by Django 3.0.2 on 2020-02-10 08:49

from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from roster import models as r_models
from departments.models import Department
from timesheet import models as ts_models
from messageboard.models import Board

GROUPS_PERMISSIONS = {
    "worker": {
        Department: ["view"],
        r_models.Shift: ["view"],
        ts_models.Stamp: ["view"],
        ts_models.Time: ["view"],
        Board: ["view"]
    },
    "shift_leader": {
        r_models.Shift: ["view", "add", "change", "delete"],
        Department: ["view"],
        ts_models.Stamp: ["view"],
        ts_models.Time: ["view", "add", "change", "delete"],
        User: ["view"]
    },
    "supervisor": {
        r_models.Shift: ["view", "add", "change", "delete"],
        Department: ["view", "add", "change", "delete"],
        ts_models.Time: ["view", "add", "change", "delete"],
        ts_models.Stamp: ["view", "add", "change", "delete"],
        ts_models.AdditionalRate: ["view", "add", "change", "delete"],
        User: ["view", "add", "change", "delete"]
    }
}

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create default groups"

    def handle(self, *args, **options):
        # Loop groups
        for group_name in GROUPS_PERMISSIONS:

            # Get or create group
            group, created = Group.objects.get_or_create(name=group_name)

            # Loop models in group
            for model_cls in GROUPS_PERMISSIONS[group_name]:

                # Loop permissions in group/model
                for perm_index, perm_name in enumerate(GROUPS_PERMISSIONS[group_name][model_cls]):

                    # Generate permission name as Django would generate it
                    codename = f"{perm_name}_{model_cls._meta.model_name}"

                    try:
                        # Find permission object and add to group
                        perm = Permission.objects.filter(codename=codename)
                        group.permissions.add(*perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(f"{codename} not found")
