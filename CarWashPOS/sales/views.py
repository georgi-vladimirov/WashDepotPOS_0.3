import http
import logging
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal

from core.selectors import get_cal_event_by_id
from .forms import AddSaleForm, AddServiceForm
from .selectors import get_sales_by_cal_event, get_sale_by_id, get_discount_for_subscriber_from_sale
from .services import create_sale, delete_sale, select_services_for_sale, create_cart_for_sale

logger = logging.getLogger("sales.services")


class SalesOverview(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)

        if cal_event is None:
            return render(request, "sales/sales_overview.html")

        sales = get_sales_by_cal_event(cal_event=cal_event)

        return render(request, "sales/sales_overview.html", {"sales": sales})


class AddSale(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if cal_event is None:
            logger.warning("Attempt to access AddSale view without a calendar event in session")
            return HttpResponse("No calendar event selected", status=http.HTTPStatus.BAD_REQUEST)

        location = cal_event.location
        form = AddSaleForm(location=location)

        return render(request, "sales/add_sale.html", {"form": form})

    def post(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if cal_event is None:
            messages.error(request, "No calendar event selected")
            logger.warning("Attempt to submit AddSale form without a calendar event in session")
            return redirect("sales:sales_overview")

        location = cal_event.location
        form = AddSaleForm(request.POST, location=location)

        if form.is_valid():
            sale = create_sale(form=form, cal_event=cal_event)
            return HttpResponse("<script>window.opener.location.reload(); window.close();</script>")
        else:
            logger.warning("AddSale form submission with invalid data: %s", form.errors)
            messages.error(request, "Error recording sale. Please check the form for errors.")

        return render(request, "sales/add_sale.html", {"form": form})


class DeleteSale(LoginRequiredMixin, View):
    def get(self, request, sale_id):
        sale = get_sale_by_id(sale_id=sale_id)
        if sale is None:
            messages.error(request, "Sale not found")
            return redirect("sales:sales_overview")

        if delete_sale(sale_id=sale_id):
            messages.success(request, "Sale deleted successfully")
        else:
            messages.error(request, "Error deleting sale")

        return redirect("sales:sales_overview")


class AddCart(LoginRequiredMixin, View):
    def get(self, request, sale_id):
        sale = get_sale_by_id(sale_id=sale_id)
        if sale is None:
            messages.error(request, "Sale not found")
            return redirect("sales:sales_overview")

        services_by_type = select_services_for_sale(sale=sale)
        discount = get_discount_for_subscriber_from_sale(sale=sale)

        return render(
            request,
            "sales/add_cart.html",
            {"sale_id": sale_id, "services_by_type": services_by_type, "discount": discount},
        )

    def post(self, request, sale_id):
        sale = get_sale_by_id(sale_id=sale_id)
        if sale is None:
            messages.error(request, "Sale not found")
            return redirect("sales:sales_overview")

        total_amount = Decimal(request.POST.get("total_amount"))
        discount_per = Decimal(request.POST.get("discount"))
        final_amount = Decimal(request.POST.get("final_amount"))
        service_ids = request.POST.getlist("services")  # ["3", "7", "12"]
        create_cart_for_sale(
            sale=sale,
            service_ids=service_ids,
            total_amount=total_amount,
            discount_per=discount_per,
            final_amount=final_amount,
        )

        return HttpResponse("<script>window.opener.location.reload(); window.close();</script>")
