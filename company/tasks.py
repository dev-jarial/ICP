import asyncio
import json

from celery import shared_task
from django.db import connections, transaction

from utils.web_crawler import main

from .models import Company


@shared_task(time_limit=600)
def process_uploaded_file(valid_urls):
    for website_link in valid_urls:
        try:
            print(f"Processing: {website_link}")

            # Ensure Celery correctly manages the database connection
            connections.close_all()

            # Run the web scraper
            scraped_data = asyncio.run(main(url=website_link))
            print(f"Scraped data: {scraped_data}")

            # Ensure scraped_data is a dictionary
            if isinstance(scraped_data, str):
                try:
                    scraped_data = json.loads(scraped_data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON returned for {website_link}: {scraped_data}")
                    continue  # Skip invalid responses

            if not isinstance(scraped_data, dict):
                print(f"Unexpected return type from scraper: {type(scraped_data)}")
                continue

            # Ensure atomic database transaction
            with transaction.atomic():
                Company.objects.update_or_create(
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
                        "key_capabilities": scraped_data.get("key_capabilities", []),
                        "products": scraped_data.get("products", []),
                        "industry_types": scraped_data.get("industry_types", []),
                        "partner_category": scraped_data.get("partner_category", []),
                        "number_of_years": scraped_data.get("number_of_years", None),
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
                        "oems_working_with": scraped_data.get("oems_working_with", []),
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

        except Exception as e:
            print(f"Scraping error for {website_link}: {e}")
            continue  # Skip if scraping fails
