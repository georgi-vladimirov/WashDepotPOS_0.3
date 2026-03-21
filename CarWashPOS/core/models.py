from django.db import models
from decimal import Decimal
from common.models import BaseModel


class Location(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=4, unique=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.short_name}"


class VehicleType(BaseModel):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return self.name


class ServiceType(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    name_BG = models.CharField(max_length=100, unique=True, default="")
    selectivity = models.IntegerField(default=1)
    order = models.IntegerField(default=1)

    def __str__(self) -> str:
        return self.name


class Service(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE,
        related_name="services",
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True)

    # def __str__(self) -> str:
    #     return f"{self.name} | Active: {self.is_active}"  # This will display the service name in the admin


class ServicePrice(BaseModel):
    location = models.ManyToManyField(Location, related_name="service_prices")
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    service = models.ForeignKey("Service", on_delete=models.CASCADE, related_name="service_prices")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    IMMUTABLE_FIELDS = {"vehicle_type_id", "service_id", "amount"}

    def save(self, *args, **kwargs):
        if self.pk:
            original = ServicePrice.objects.get(pk=self.pk)
            changed = {f for f in self.IMMUTABLE_FIELDS if getattr(self, f) != getattr(original, f)}
            if changed:
                raise ValueError(f"ServicePrice fields {changed} cannot be modified after creation.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()

    def __str__(self) -> str:
        locations = ", ".join([loc.name for loc in self.location.all()])
        return f"{self.service.name} - {self.vehicle_type.name} @ {locations}: {self.amount} | Active: {self.is_active}"


class VehicleBrand(BaseModel):
    brand = models.CharField(max_length=50, unique=True)
    number_sort = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.number_sort}. {self.brand}"


class EmployeePosition(BaseModel):
    position = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.position} | Active: {self.is_active}"


class Employee(BaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=15, unique=True)
    position = models.ForeignKey(EmployeePosition, on_delete=models.CASCADE, related_name="employees")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="employees")
    salary_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0))
    bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0))

    def __str__(self) -> str:
        return f"{self.employee_id} ({self.first_name} {self.last_name}) | {self.position.position} | {self.location.short_name} | Active: {self.is_active}"


class Subscriber(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0))
    location = models.ManyToManyField(Location, related_name="subscribers")

    def __str__(self) -> str:
        return f"{self.name} - {self.discount_percentage}% - Active: {self.is_active}"


class CalendarEvent(BaseModel):
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, unique_for_date="date")

    class Meta:
        unique_together = ("date", "location")

    def __str__(self) -> str:
        return f"{self.date} - {self.location.name} - Active: {self.is_active}"
