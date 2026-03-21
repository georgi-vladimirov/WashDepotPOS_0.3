from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

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


# Resource classes for import/export
class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service
        fields = ("name", "service_type", "description", "active")
        import_id_fields = ("name",)  # Use name as unique identifier
        skip_unchanged = True
        report_skipped = True


class ServicePriceResource(resources.ModelResource):
    def dehydrate_service(self, service_price):
        return service_price.service.name if service_price.service else ""

    def dehydrate_vehicle_type(self, service_price):
        return service_price.vehicle_type.name if service_price.vehicle_type else ""

    def dehydrate_location(self, service_price):
        return "|".join([loc.name for loc in service_price.location.all()])

    def before_import_row(self, row, row_number=None, **kwargs):
        # Don't process the location field yet - we'll add all active locations automatically
        if "location" in row:
            row.pop("location")
        self._temp_location = None

        # Convert service name to ID
        if "service" in row:
            try:
                service_obj = Service.objects.get(name=row["service"])
                row["service"] = service_obj.pk
            except Service.DoesNotExist:
                raise ValueError(f"Service '{row['service']}' not found")

        # Convert vehicle_type name to ID
        if "vehicle_type" in row:
            try:
                vehicle_type_obj = VehicleType.objects.get(name=row["vehicle_type"])
                row["vehicle_type"] = vehicle_type_obj.pk
            except VehicleType.DoesNotExist:
                raise ValueError(f"Vehicle type '{row['vehicle_type']}' not found")

    def after_save_instance(self, instance, row, using_transactions, dry_run, **kwargs):
        if not dry_run:
            # Add all active locations automatically
            active_locations = Location.objects.filter(is_active=True)
            instance.location.set(active_locations)

    class Meta:
        model = ServicePrice
        fields = ("service", "vehicle_type", "amount", "is_active")
        export_order = ("service", "vehicle_type", "location", "amount", "is_active")
        exclude = ("id",)
        import_id_fields = []


@admin.register(Service)
class ServicesAdmin(ImportExportModelAdmin):
    resource_class = ServiceResource
    list_display = ("name", "service_type", "is_active")
    list_filter = ("service_type", "is_active")
    search_fields = ("name", "description")


@admin.register(ServicePrice)
class ServicePriceAdmin(ImportExportModelAdmin):
    resource_class = ServicePriceResource
    list_display = ("service__name", "vehicle_type__name", "amount", "is_active", "get_locations")
    list_filter = ("location", "vehicle_type", "is_active")
    search_fields = ("service__name",)

    def get_locations(self, obj):
        return ", ".join([loc.name for loc in obj.location.all()])

    get_locations.short_description = "Locations"


# Register remaining models
admin.site.register(Location)
admin.site.register(VehicleType)
admin.site.register(ServiceType)
admin.site.register(VehicleBrand)
admin.site.register(EmployeePosition)
admin.site.register(Employee)
admin.site.register(Subscriber)
admin.site.register(CalendarEvent)
