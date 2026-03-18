from django.db import models
from django.contrib.auth.models import Group
from core.models import Location


class GroupProfile(models.Model):
    """Extends Django's built-in Group with a Location."""

    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="profile")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="groups")

    def __str__(self):
        return f"{self.group.name} - {self.location.name}"