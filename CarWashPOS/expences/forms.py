from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Expence
from cal_app.models import CalendarEvent


class AddExpenceForm(forms.ModelForm):
    def __init__(self, *args, date: CalendarEvent, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize fields
        self.date = self.fields["date"]
        self.date.initial = date
        self.date.widget = forms.HiddenInput()

    class Meta:
        model = Expence
        fields = ["date", "amount", "name", "details"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "name": _("Name"),
            "amount": _("Amount"),
            "details": _("Details"),
        }

        error_messages = {
            "amount": {
                "required": "Please enter an amount.",
                "invalid": "Enter a valid amount.",
            },
        }
