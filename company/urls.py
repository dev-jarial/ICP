from django.urls import path

from . import views

app_name = "company"  # Namespace for URL reversing

urlpatterns = [
    # Main entry point - company details form
    path("", views.company_form_view, name="company_form"),
    # Optional additional URLs you might want to add
    # path('list/', views.company_list_view, name='company_list'),
    # path('detail/<int:pk>/', views.company_detail_view, name='company_detail'),
]
