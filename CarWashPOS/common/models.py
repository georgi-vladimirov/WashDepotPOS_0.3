from django.db import models


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This makes it an abstract base class and won't create a separate DB table
