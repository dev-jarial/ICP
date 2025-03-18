import asyncio
import json

import pandas as pd
import validators
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render

from utils.web_crawler import main

from .forms import CompanyForm, CompanyUploadForm
from .models import Company
from .tasks import process_uploaded_file


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
                try:
                    # Run the scraper function
                    scraped_data = asyncio.run(main(url=website_link))

                    # Ensure JSON is properly formatted
                    if isinstance(scraped_data, str):
                        scraped_data = json.loads(scraped_data)
                    # Save scraped data to the database
                    company, created = Company.objects.update_or_create(
                        website_link=website_link,
                        defaults={
                            "name": scraped_data.get("name"),
                            "email": scraped_data.get("email"),
                            "mobile_number": scraped_data.get("mobile_number"),
                            "general_contact_number": scraped_data.get(
                                "general_contact_number"
                            ),
                            "hq_address": scraped_data.get("hq_address"),
                            "locations": scraped_data.get("locations_offices"),
                            "key_capabilities": scraped_data.get("key_capabilities"),
                            "products": scraped_data.get("products"),
                            "industry_types": scraped_data.get("industry_types"),
                            "partner_category": scraped_data.get("partner_category"),
                            "number_of_years": scraped_data.get("number_of_years"),
                            "number_of_customers": scraped_data.get(
                                "number_of_customers"
                            ),
                            "number_of_employees": scraped_data.get(
                                "number_of_employees"
                            ),
                            "top_customer_names": scraped_data.get(
                                "top_customer_names"
                            ),
                            "case_studies_available": scraped_data.get(
                                "case_studies_available"
                            ),
                            "product_brochure_link": scraped_data.get(
                                "product_brochure"
                            ),
                            "client_testimonials": scraped_data.get(
                                "client_testimonials"
                            ),
                            "oems_working_with": scraped_data.get("oems_working_with"),
                            "brief_company_profile": scraped_data.get(
                                "brief_company_profile"
                            ),
                            "top_management_details": scraped_data.get(
                                "top_management_details"
                            ),
                            "annual_revenue": scraped_data.get("annual_revenue"),
                            "average_deal_size": scraped_data.get("average_deal_size"),
                            "operating_countries": scraped_data.get(
                                "operating_countries"
                            ),
                            "funding_status": scraped_data.get("funding_status"),
                            "google_rating": scraped_data.get("google_rating"),
                        },
                    )

                except Exception as e:
                    print(e)
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


@staff_member_required
def upload_company_file(request):
    if request.method == "POST":
        form = CompanyUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_instance = form.save()
            file_path = upload_instance.file.path

            try:
                # Read CSV or Excel file
                df = (
                    pd.read_csv(file_path, header=None)
                    if file_path.endswith(".csv")
                    else pd.read_excel(file_path, header=None)
                )
                df = df.dropna().reset_index(drop=True)

                # Ensure valid structure
                if df.empty or df.shape[1] != 1:
                    messages.error(
                        request, "The file should contain exactly one column with URLs."
                    )
                    return redirect("company:upload_company_file")

                # Extract and validate URLs
                valid_urls = [
                    str(row.iloc[0]).strip()
                    for _, row in df.iterrows()
                    if validators.url(str(row.iloc[0]).strip())
                ]

                if not valid_urls:
                    messages.warning(
                        request, "No valid website URLs found in the file."
                    )
                    return redirect("company:upload_company_file")

                # Run the processing in the background using Celery
                process_uploaded_file.delay(valid_urls)

                # Send response immediately with the count of valid URLs
                messages.success(
                    request,
                    f"Total {len(valid_urls)} valid URLs found. Processing in background.",
                )

                return redirect("company:upload_company_file")

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
                return redirect("company:upload_company_file")

        else:
            messages.error(
                request, "Invalid file format. Please upload a CSV or Excel file."
            )

    else:
        form = CompanyUploadForm()

    return render(request, "admin/upload_company_file.html", {"form": form})
