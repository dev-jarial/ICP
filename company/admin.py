import csv

import openpyxl
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html

from .models import Company


@admin.action(description="Export selected companies as CSV")
def export_as_csv(modeladmin, request, queryset):
    """Export selected company data as CSV"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=selected_companies.csv"

    writer = csv.writer(response)

    # Define headers
    headers = [
        field.name for field in Company._meta.fields
    ]  # Fetch all field names dynamically
    writer.writerow(headers)

    # Write data rows
    for company in queryset:
        row = [getattr(company, field) for field in headers]
        writer.writerow(row)

    return response


@admin.action(description="Export selected companies as Excel")
def export_as_excel(modeladmin, request, queryset):
    """Export selected company data as Excel"""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Companies"

    # Define headers
    headers = [
        field.name for field in Company._meta.fields
    ]  # Fetch all field names dynamically
    sheet.append(headers)

    # Add data rows
    for company in queryset:
        row = []
        for field in headers:
            value = getattr(company, field)
            if isinstance(value, list) or isinstance(value, dict):
                value = str(value)  # Convert JSONField data to string
            row.append(value)
        sheet.append(row)

    # Prepare the response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=selected_companies.xlsx"

    workbook.save(response)
    return response


class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "download_links")
    search_fields = ("name", "email")
    actions = [export_as_csv, export_as_excel]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("export/csv/", self.export_all_as_csv, name="export_csv"),
            path("export/excel/", self.export_all_as_excel, name="export_excel"),
        ]
        return custom_urls + urls

    def export_all_as_csv(self, request):
        """Export all company data as CSV"""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=all_companies.csv"

        writer = csv.writer(response)

        headers = [
            field.name for field in Company._meta.fields
        ]  # Fetch all field names dynamically
        writer.writerow(headers)

        for company in Company.objects.all():
            row = [getattr(company, field) for field in headers]
            writer.writerow(row)

        return response

    def export_all_as_excel(self, request):
        """Export all company data as Excel"""
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Companies"

        headers = [
            field.name for field in Company._meta.fields
        ]  # Fetch all field names dynamically
        sheet.append(headers)

        for company in Company.objects.all():
            row = []
            for field in headers:
                value = getattr(company, field)
                if isinstance(value, list) or isinstance(value, dict):
                    value = str(value)  # Convert JSONField data to string
                row.append(value)
            sheet.append(row)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=all_companies.xlsx"

        workbook.save(response)
        return response

    def download_links(self, obj):
        """Adds download buttons in the admin panel"""
        csv_url = "/admin/company/company/export/csv/"
        excel_url = "/admin/company/company/export/excel/"
        return format_html(
            f'<a href="{csv_url}">📥 Download CSV</a> | <a href="{excel_url}">📥 Download Excel</a>'
        )

    download_links.allow_tags = True
    download_links.short_description = "Download Table"


admin.site.register(Company, CompanyAdmin)
