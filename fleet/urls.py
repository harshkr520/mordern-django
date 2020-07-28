# -*- coding: utf-8 -*-

from . import views
from django.urls import path

urlpatterns = [
    path('receipt/add', views.add_fuel_receipt_records),
    path('type', views.get_fuel_types),
    path('get/<driverid>', views.get_driver_fuel_stats)
    ]