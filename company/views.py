import asyncio
import json

import pandas as pd
import validators
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render

from utils.google_rating import google_rating
from utils.list_str import listToStr
from utils.script import Crawler
from utils.youtube import get_videos_from_query

from .forms import CompanyForm, CompanyUploadForm
from .models import Company
from .tasks import process_uploaded_file


def company_form_view(request):
    format_data = None
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
                    scraped_data = asyncio.run(Crawler(url=website_link).start())
                    # Ensure JSON is properly formatted
                    if isinstance(scraped_data, str):
                        scraped_data = json.loads(scraped_data)
                    # Save scraped data to the database
                    format_data = {
                        "name": scraped_data.get("name"),
                        "email": scraped_data.get("email"),
                        "mobile_number": scraped_data.get("mobile_number"),
                        "general_contact_number": scraped_data.get(
                            "general_contact_number"
                        ),
                        "hq_address": listToStr(scraped_data.get("hq_address")),
                        "locations": listToStr(scraped_data.get("locations_offices")),
                        "key_capabilities": listToStr(
                            scraped_data.get("key_capabilities")
                        ),
                        "products": listToStr(scraped_data.get("products")),
                        "industry_types": listToStr(scraped_data.get("industry_types")),
                        "partner_category": listToStr(
                            scraped_data.get("partner_category")
                        ),
                        "number_of_years": scraped_data.get("number_of_years"),
                        "number_of_customers": scraped_data.get("number_of_customers"),
                        "number_of_employees": scraped_data.get("number_of_employees"),
                        "top_customer_names": listToStr(
                            scraped_data.get("top_customer_names")
                        ),
                        "case_studies": listToStr(scraped_data.get("case_studies")),
                        "product_brochure_link": scraped_data.get("product_brochure"),
                        "client_testimonials": listToStr(
                            scraped_data.get("client_testimonials")
                        ),
                        "oems_working_with": listToStr(
                            scraped_data.get("oems_working_with")
                        ),
                        "oem_partnership_status": listToStr(
                            scraped_data.get("oem_partnership_status")
                        ),
                        "brief_company_profile": scraped_data.get(
                            "brief_company_profile"
                        ),
                        "top_management_details": listToStr(
                            scraped_data.get("top_management_details")
                        ),
                        "annual_revenue": scraped_data.get("annual_revenue"),
                        "average_deal_size": scraped_data.get("average_deal_size"),
                        "operating_countries": listToStr(
                            scraped_data.get("operating_countries")
                        ),
                        "funding_status": scraped_data.get("funding_status"),
                        "youtube_videos": listToStr(
                            get_videos_from_query(
                                query=scraped_data.get("youtube_query"), n=2
                            )
                        ),
                        "google_rating": google_rating(scraped_data.get("name")),
                    }
                    company, created = Company.objects.update_or_create(
                        website_link=website_link,
                        defaults=format_data,
                    )
                except Exception as e:
                    print(e)
                    error = f"Failed to scrape data: {str(e)}"

    return render(
        request,
        "company/company_form.html",
        {
            "form": form,
            "scraped_data": format_data,
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
                    pd.read_csv(file_path, header=None, dtype=str)
                    if file_path.endswith(".csv")
                    else pd.read_excel(file_path, header=None, dtype=str)
                )
                df = df.dropna(how="all").reset_index(drop=True)  # remove empty rows

                # Ensure valid structure
                if df.empty:
                    messages.error(
                        request, "The file is empty or does not contain valid data."
                    )
                    return redirect("company:upload_company_file")

                # Extract and validate all URLs from all the columns
                valid_urls = set()

                for _, row in df.iterrows():
                    for value in row:
                        if isinstance(value, str):
                            value = value.strip()
                            if validators.url(value):
                                print(value)
                                valid_urls.add(value)

                if not valid_urls:
                    messages.warning(
                        request, "No valid website URLs found in the file."
                    )
                    return redirect("company:upload_company_file")

                # Convert set to list and send to Celery task
                valid_urls_list = list(valid_urls)
                process_uploaded_file.delay(valid_urls_list)

                # Send response immediately with the count of valid URLs
                messages.success(
                    request,
                    f"Total {len(valid_urls_list)} valid URLs found. Processing in background.",
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
