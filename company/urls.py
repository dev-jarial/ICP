from django.conf.urls.static import static
from django.urls import path

from icp import settings

from . import views

app_name = "company"  # Namespace for URL reversing

urlpatterns = [
    # Main entry point - company details form
    path("", views.company_form_view, name="company_form"),
    path("upload/", views.upload_company_file, name="upload_company_file"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
