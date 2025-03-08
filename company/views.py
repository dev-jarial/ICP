import asyncio
import json

import validators
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render

from utils.web_crawler import main

from .forms import CompanyForm, CompanyUploadForm
from .models import Company


def company_form_view(request):
    scraped_data = None
    message = None
    error = None
    form = CompanyForm(request.POST or None)  # Load form data properly

    if request.method == "POST":
        if form.is_valid():  # Ensure form validation
            website_link = form.cleaned_data["website_link"]
            if not validators.url(website_link):
                error = "Invalid website URL. Please enter a valid link."
            else:
                # Try to retrieve the existing company data
                # existing_company = Company.objects.filter(
                #     website_link=website_link
                # ).first()

                # if existing_company:
                #     # Convert the company object into a dictionary for rendering
                #     scraped_data = {
                #         "name": existing_company.name,
                #         "email": existing_company.email,
                #         "mobile_number": existing_company.mobile_number,
                #         "general_contact_number": existing_company.general_contact_number,
                #         "hq_address": existing_company.hq_address,
                #         "locations": existing_company.locations,
                #         "key_capabilities": existing_company.key_capabilities,
                #         "products": existing_company.products,
                #         "industry_types": existing_company.industry_types,
                #         "partner_category": existing_company.partner_category,
                #         "number_of_years": existing_company.number_of_years,
                #         "number_of_customers": existing_company.number_of_customers,
                #         "number_of_employees": existing_company.number_of_employees,
                #         "top_customer_names": existing_company.top_customer_names,
                #         "case_studies_available": existing_company.case_studies_available,
                #         "product_brochure": existing_company.product_brochure_link,
                #         "client_testimonials": existing_company.client_testimonials,
                #         "oems_working_with": existing_company.oems_working_with,
                #         "brief_company_profile": existing_company.brief_company_profile,
                #         "top_management_details": existing_company.top_management_details,
                #         "annual_revenue": existing_company.annual_revenue,
                #         "average_deal_size": existing_company.average_deal_size,
                #         "operating_countries": existing_company.operating_countries,
                #         "funding_status": existing_company.funding_status,
                #         "google_rating": existing_company.google_rating,
                #     }
                #     message = "Company data retrieved from database."

                # else:
                try:
                    # Run the scraper function
                    scraped_data = asyncio.run(main(url=website_link))

                    # Ensure JSON is properly formatted
                    if isinstance(scraped_data, str):
                        scraped_data = json.loads(scraped_data)

                    print("Scraped Data:", scraped_data)  # Debugging output

                    # Save scraped data to the database
                    company, created = Company.objects.update_or_create(
                        website_link=website_link,
                        defaults={
                            "name": scraped_data.get("name", ""),
                            "email": scraped_data.get("email_id", None),
                            "mobile_number": scraped_data.get("mobile_number", None),
                            "general_contact_number": scraped_data.get(
                                "general_contact_number", None
                            ),
                            "hq_address": scraped_data.get("hq_address", []),
                            "locations": scraped_data.get("locations_offices", []),
                            "key_capabilities": scraped_data.get(
                                "key_capabilities", []
                            ),
                            "products": scraped_data.get("products", []),
                            "industry_types": scraped_data.get("industry_types", []),
                            "partner_category": scraped_data.get(
                                "partner_category", []
                            ),
                            "number_of_years": scraped_data.get(
                                "number_of_years", None
                            ),
                            "number_of_customers": scraped_data.get(
                                "number_of_customers", None
                            ),
                            "number_of_employees": scraped_data.get(
                                "number_of_employees", None
                            ),
                            "top_customer_names": scraped_data.get(
                                "top_customer_names", []
                            ),
                            "case_studies_available": scraped_data.get(
                                "case_studies_available", []
                            ),
                            "product_brochure_link": scraped_data.get(
                                "product_brochure", None
                            ),
                            "client_testimonials": scraped_data.get(
                                "client_testimonials", []
                            ),
                            "oems_working_with": scraped_data.get(
                                "oems_working_with", []
                            ),
                            "brief_company_profile": scraped_data.get(
                                "brief_company_profile", None
                            ),
                            "top_management_details": scraped_data.get(
                                "top_management_details", []
                            ),
                            "annual_revenue": scraped_data.get("annual_revenue", None),
                            "average_deal_size": scraped_data.get(
                                "average_deal_size", None
                            ),
                            "operating_countries": scraped_data.get(
                                "operating_countries", []
                            ),
                            "funding_status": scraped_data.get("funding_status", None),
                            "google_rating": scraped_data.get("google_rating", None),
                        },
                    )

                    message = "New company data saved successfully!"

                except Exception as e:
                    error = f"Failed to scrape data: {str(e)}"

    return render(
        request,
        "company/company_form.html",
        {
            "form": form,
            "scraped_data": scraped_data,
            "message": message,
            "error": error,
        },
    )


@staff_member_required  # Ensures only admins can access
def upload_company_file(request):
    if request.method == "POST":
        form = CompanyUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "File uploaded successfully.")
            return redirect("company:upload_company_file")  # Redirect to the same page
        else:
            messages.error(request, "Invalid file. Please upload a CSV or Excel file.")
    else:
        form = CompanyUploadForm()

    return render(request, "admin/upload_company_file.html", {"form": form})
