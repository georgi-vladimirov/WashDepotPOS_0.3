from django.contrib import admin

from .models import (
    Location,
    VehicleType,
    ServicePrice,
    ServiceType,
    Service,
    VehicleBrand,
    EmployeePosition,
    Employee,
    Subscriber,
    CalendarEvent,
)

admin.site.register(Location)
admin.site.register(VehicleType)
admin.site.register(ServicePrice)
admin.site.register(ServiceType)
admin.site.register(Service)
admin.site.register(VehicleBrand)
admin.site.register(EmployeePosition)
admin.site.register(Employee)
admin.site.register(Subscriber)
admin.site.register(CalendarEvent)