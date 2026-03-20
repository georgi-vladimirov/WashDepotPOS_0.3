from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Sale
from core.models import CalendarEvent, VehicleBrand, VehicleType, Subscriber, Employee, Location
from core.selectors import (
    get_vehicle_brands,
    get_vehicle_types,
    get_employees_by_location_and_position,
    get_subscribers_by_location,
)


class AddSaleForm(forms.ModelForm):
    def __init__(self, *args, location: Location, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter vehicle brands to only show active ones
        brands = get_vehicle_brands(is_active=True)
        self.fields["vehicle_brand"].queryset = brands  # type: ignore
        # Show only brand name, not the complete string
        self.fields["vehicle_brand"].label_from_instance = lambda obj: obj.brand  # type: ignore

        vehicle_types = get_vehicle_types(is_active=True)
        self.fields["vehicle_type"].queryset = vehicle_types  # type: ignore
        # Show only vehicle type name, not the complete string
        self.fields["vehicle_type"].label_from_instance = lambda obj: obj.name  # type: ignore

        manager = get_employees_by_location_and_position(is_active=True, location=location, position="Manager")
        self.fields["manager"].queryset = manager  # type: ignore
        # Show only vehicle type name, not the complete string
        self.fields["manager"].label_from_instance = lambda obj: obj.employee_id  # type: ignore

        worker = get_employees_by_location_and_position(is_active=True, location=location, position="Worker")
        self.fields["worker"].queryset = worker  # type: ignore
        # Show only worker name, not the complete string
        self.fields["worker"].label_from_instance = lambda obj: obj.employee_id  # type: ignore

        subscriber = get_subscribers_by_location(is_active=True, location=location)
        self.fields["subscriber"].queryset = subscriber  # type: ignore
        # Show only subscriber name, not the complete string
        self.fields["subscriber"].label_from_instance = lambda obj: f"{obj.name} - {obj.discount_percentage}%"  # type: ignore
        # Add data attribute with discount percentage
        self.fields["subscriber"].widget.attrs["data-discount"] = True

    class Meta:
        model = Sale
        fields = [
            "vehicle_brand",
            "vehicle_type",
            "reg_number",
            "manager",
            "worker",
            "subscriber",
        ]
        widgets = {
            "vehicle_brand": forms.Select(attrs={"class": "form-select"}),
            "vehicle_type": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "reg_number": forms.TextInput(attrs={"class": "form-control"}),
            "manager": forms.Select(attrs={"class": "form-select"}),
            "worker": forms.Select(attrs={"class": "form-select"}),
            "subscriber": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
        "vehicle_brand": _("Brand"),
        "vehicle_type": _("Vehicle Type"),
        "reg_number": _("Reg. Number"),
        "manager": _("Manager"),
        "worker": _("Worker"),
        "subscriber": _("Subscriber"),
        }
