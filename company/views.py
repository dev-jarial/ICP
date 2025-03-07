import asyncio
import json

import validators
from django.shortcuts import render

from utils.web_crawler import main

from .forms import CompanyForm
from .models import Company


def company_form_view(request):
    scraped_data = None
    message = None
    error = None

    if request.method == "POST":
        form = CompanyForm(request.POST)

        if form.is_valid():
            website_link = form.cleaned_data["website_link"]

            if not validators.url(website_link):
                error = "Invalid website URL. Please enter a valid link."
            else:
                try:
                    # Run the scraper function
                    scraped_data = asyncio.run(main(url=website_link))

                    # Ensure JSON is properly formatted
                    if isinstance(scraped_data, str):
                        scraped_data = json.loads(scraped_data)

                    print("Scraped Data:", scraped_data)  # Debugging output

                    # Check if the company already exists
                    company, created = Company.objects.update_or_create(
                        website_link=website_link,
                        defaults={
                            "name": scraped_data.get("company_name", ""),
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

                    if created:
                        message = "New company data saved successfully!"
                    else:
                        message = "Company data updated successfully!"

                except Exception as e:
                    print(f"{e= }")
                    error = f"Failed to scrape data: {str(e)}"

    else:
        form = CompanyForm()

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
