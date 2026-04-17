from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import (
    Location,
    CalendarEvent,
    VehicleType,
    ServicePrice,
    ServiceType,
    Service,
    VehicleBrand,
    EmployeePosition,
    Employee,
    Subscriber,
)


# Resource classes for import/export
class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service
        fields = ("id", "name", "service_type", "description", "is_active")
        import_id_fields = ("name",)  # Use name as unique identifier
        export_order = ("id", "name", "service_type", "description", "is_active")
        skip_unchanged = True
        report_skipped = True


@admin.register(Service)
class ServicesAdmin(ImportExportModelAdmin):
    resource_class = ServiceResource
    list_display = ("id", "name", "service_type", "is_active")
    list_filter = ("id", "service_type", "is_active")
    search_fields = ("name", "description")


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

    def after_save_instance(self, instance, row, using_transactions, dry_run, **kwargs):  # type: ignore
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


@admin.register(ServicePrice)
class ServicePriceAdmin(ImportExportModelAdmin):
    resource_class = ServicePriceResource
    list_display = (
        "service__name",
        "vehicle_type__name",
        "amount",
        "is_active",
        "get_locations",
    )
    list_filter = ("location", "vehicle_type", "is_active")
    search_fields = ("service__name",)

    def get_locations(self, obj):
        return ", ".join([loc.name for loc in obj.location.all()])

    get_locations.short_description = "Locations"  # type: ignore


class SubscriberResource(resources.ModelResource):
    class Meta:
        model = Subscriber
        fields = ("name", "company_id", "discount_percentage", "location", "is_active")
        import_id_fields = ("name",)  # Use name as unique identifier
        export_order = (
            "name",
            "company_id",
            "discount_percentage",
            "location",
            "is_active",
        )
        skip_unchanged = True
        report_skipped = True


@admin.register(Subscriber)
class SubscriberAdmin(ImportExportModelAdmin):
    resource_class = SubscriberResource
    list_display = ("name", "company_id", "discount_percentage", "get_locations")
    search_fields = ("name", "company_id")

    def get_locations(self, obj):
        return ", ".join([loc.short_name for loc in obj.location.all()])

    get_locations.short_description = "Locations"  # type: ignore


class VehicleBrandResource(resources.ModelResource):
    class Meta:
        model = VehicleBrand
        fields = ("brand", "number_sort")
        import_id_fields = ("brand",)  # Use name as unique identifier
        export_order = ("brand", "number_sort", "is_active")
        skip_unchanged = True
        report_skipped = True


@admin.register(VehicleBrand)
class VehicleBrandAdmin(ImportExportModelAdmin):
    resource_class = VehicleBrandResource
    list_display = ("brand", "number_sort")


class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Employee
        fields = (
            "first_name",
            "last_name",
            "employee_id",
            "position",
            "location",
            "salary_percentage",
            "bonus_percentage",
            "is_active",
        )
        import_id_fields = ("employee_id",)  # Use name as unique identifier
        export_order = (
            "first_name",
            "last_name",
            "employee_id",
            "position",
            "location",
            "salary_percentage",
            "bonus_percentage",
            "is_active",
        )
        skip_unchanged = True
        report_skipped = True


@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = (
        "first_name",
        "last_name",
        "employee_id",
        "position__position",
        "location__short_name",
        "salary_percentage",
        "bonus_percentage",
        "is_active",
    )
    search_fields = ("location", "position__position")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    class Meta:
        model = Location
        fields = ("name", "short_name")
        export_order = ("id", "name", "short_name", "is_active")

    list_display = ("id", "name", "short_name", "is_active")


@admin.register(EmployeePosition)
class EmployeePositionAdmin(admin.ModelAdmin):
    class Meta:
        model = EmployeePosition
        fields = ("position", "description")
        export_order = ("id", "position", "description", "is_active")

    list_display = ("id", "position", "description", "is_active")


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    class Meta:
        model = ServiceType
        fields = ("id", "name", "name_BG", "selectivity", "order", "is_active")
        export_order = ("id", "name", "name_BG", "selectivity", "order", "is_active")

    list_display = ("id", "name", "name_BG", "selectivity", "order", "is_active")


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    class Meta:
        model = VehicleType
        fields = ("id", "name")
        export_order = ("id", "name")

    list_display = ("id", "name")


admin.site.register(CalendarEvent)
