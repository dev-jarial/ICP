import asyncio
import json

from celery import shared_task
from django.db import connections, transaction

from utils.list_str import listToStr
from utils.script import Crawler

from .models import Company


@shared_task(time_limit=600)
def process_uploaded_file(valid_urls):
    for website_link in valid_urls:
        try:
            # Ensure Celery correctly manages the database connection
            connections.close_all()

            # Run the web scraper
            scraped_data = asyncio.run(Crawler(url=website_link).start())

            # Ensure scraped_data is a dictionary
            if isinstance(scraped_data, str):
                try:
                    scraped_data = json.loads(scraped_data)
                except json.JSONDecodeError:
                    continue  # Skip invalid responses

            if not isinstance(scraped_data, dict):
                continue
            format_data = {
                "name": scraped_data.get("name"),
                "email": scraped_data.get("email"),
                "mobile_number": scraped_data.get("mobile_number"),
                "general_contact_number": scraped_data.get("general_contact_number"),
                "hq_address": listToStr(scraped_data.get("hq_address")),
                "locations": listToStr(scraped_data.get("locations_offices")),
                "key_capabilities": listToStr(scraped_data.get("key_capabilities")),
                "products": listToStr(scraped_data.get("products")),
                "industry_types": listToStr(scraped_data.get("industry_types")),
                "partner_category": listToStr(scraped_data.get("partner_category")),
                "number_of_years": scraped_data.get("number_of_years"),
                "number_of_customers": scraped_data.get("number_of_customers"),
                "number_of_employees": scraped_data.get("number_of_employees"),
                "top_customer_names": listToStr(scraped_data.get("top_customer_names")),
                "case_studies": listToStr(scraped_data.get("case_studies")),
                "product_brochure_link": scraped_data.get("product_brochure"),
                "client_testimonials": listToStr(
                    scraped_data.get("client_testimonials")
                ),
                "oems_working_with": listToStr(scraped_data.get("oems_working_with")),
                "brief_company_profile": scraped_data.get("brief_company_profile"),
                "top_management_details": listToStr(
                    scraped_data.get("top_management_details")
                ),
                "annual_revenue": scraped_data.get("annual_revenue"),
                "average_deal_size": scraped_data.get("average_deal_size"),
                "operating_countries": listToStr(
                    scraped_data.get("operating_countries")
                ),
                "funding_status": scraped_data.get("funding_status"),
                "google_rating": scraped_data.get("google_rating"),
            }
            # Ensure atomic database transaction
            with transaction.atomic():
                Company.objects.update_or_create(
                    website_link=website_link, defaults=format_data
                )

        except Exception as e:
            print(f"Scraping error for {website_link}: {e}")
            continue  # Skip if scraping fails
