from django.db import models
from typing import Any

class BaseModel(models.Model):
    """
    Abstract base model providing common fields and utilities for all models.
    """
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    display_fields: list[str] = [] #Used to define which fields to include in logger data
    def logger_data(self):
        data: dict[str, str] = {"id": str(self.pk), "created_at": str(self.date_created)}
        for field_name in self.display_fields:
            try:
                value = getattr(self, field_name)
                # UUID & Decimal
                if hasattr(value, 'hex'):   # UUID
                    value = str(value)
                elif hasattr(value, 'quantize'):    # Decimal
                    value = float(value)
                data[field_name] = str(value)
            except AttributeError:
                pass
        return data

    class Meta:
        abstract = True  # This makes it an abstract base class and won't create a separate DB table
