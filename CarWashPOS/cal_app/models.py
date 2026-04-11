from django.db import models
from common.models import BaseModel
from core.models import Location


class CalendarEvent(BaseModel):
    date = models.DateField()
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, unique_for_date="date"
    )
    ################
    display_fields: list[str] = ["date", "location"]

    ################
    class Meta(BaseModel.Meta):
        unique_together = ("date", "location")

    def __str__(self) -> str:
        return f"{self.date} - {self.location.name}"
