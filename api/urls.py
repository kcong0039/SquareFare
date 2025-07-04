# scanner_app/urls.py

from django.urls import path
from backend.views import latest_scan_view

urlpatterns = [
    path("api/latest-scan/", latest_scan_view),
]