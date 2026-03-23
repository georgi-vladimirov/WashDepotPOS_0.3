from decimal import Decimal
from django import forms
from django.forms.widgets import Widget
from django.utils.translation import gettext_lazy as _
from core.models import Employee, CalendarEvent
from sales.models import Sale
from .models import Transaction, PaymentMethod, Origin, TranType

from typing import cast
from django.forms import ModelChoiceField


class TransactionForm(forms.ModelForm):
    def __init__(self, *args,
        amount:Decimal = Decimal("0.00"),
        type: TranType|None = None,
        origin: Origin|None = None,
        sale: Sale|None = None,
        employee: Employee|None = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        # Initialize fields
        self.date = self.fields["date"]
        self.date.widget = forms.HiddenInput()
        self.amount = self.fields["amount"]
        self.type = self.fields["type"]
        self.origin = self.fields["origin"]
        self.payment_method = self.fields["payment_method"]
        self.sale = self.fields["sale"]
        self.employee = self.fields["employee"]

        if sale:
            self.set_for_sale(amount, sale)

        if employee:
            self.set_for_employee(employee)

    def set_for_employee(self, employee: Employee):
        # Set initial amounts for Employee
        self.type.initial = TranType.OUT
        self.type.widget = forms.HiddenInput()
        self.payment_method.initial = PaymentMethod.CASH
        self.payment_method.widget = forms.HiddenInput()

        # use a properly typed reference so static checkers accept label_from_instance
        employee_field = cast(ModelChoiceField, self.employee)
        employee_field.initial = employee
        employee_field.label_from_instance = lambda obj: f"{obj.employee_id}"
        employee_field.widget = forms.HiddenInput()


    def set_for_sale(self, amount:Decimal, sale:Sale):
        # Set initial amounts for Sales
        self.amount.initial = amount
        self.type.initial = TranType.IN
        self.type.widget = forms.HiddenInput()
        self.origin.initial = Origin.INCOME
        self.origin.widget = forms.HiddenInput()
        self.sale.initial = sale
        self.sale.widget = forms.HiddenInput()
        self.employee.widget = forms.HiddenInput()

    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'type', 'origin', 'payment_method', 'sale', 'employee']
        widgets = {
            'amount': forms.NumberInput(attrs={"class": "form-control", 'step': '0.01'}),
            'type': forms.Select(attrs={"class": "form-control"}),
            'origin': forms.Select(attrs={"class": "form-control"}),
            'payment_method': forms.Select(attrs={"class": "form-control"}),
            'sale': forms.Select(attrs={"class": "form-control"}),
            'employee': forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            'amount': _('Amount'),
            'payment_method': _('Payment Method'),
        }
        error_messages = {
                    "amount": {
                        "required": "Please enter an amount.",
                        "invalid": "Enter a valid amount.",
                    },
                    "origin": {"required": "Please select a payment origin."},
                    "payment_method": {"required": "Please select a payment method."},
                }
