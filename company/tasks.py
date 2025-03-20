import asyncio
import json
import logging
from asyncio.exceptions import TimeoutError

from celery import shared_task
from django.db import connections, transaction

from utils.list_str import listToStr
from utils.script import Crawler

from .models import Company

# Set up logging
logger = logging.getLogger(__name__)

# Set an explicit timeout for the scraper (e.g., 30 seconds)
SCRAPER_TIMEOUT = 150


@shared_task(time_limit=600)
def process_uploaded_file(valid_urls):
    for website_link in valid_urls:
        try:
            # Ensure database connections are managed correctly
            connections.close_all()
            logger.info(f"🚀 Processing: {website_link}")

            # Run the scraper asynchronously
            scraped_data = asyncio.run(scrape_with_timeout(website_link))

            # Ensure scraped_data is a valid JSON object
            if isinstance(scraped_data, str):
                try:
                    scraped_data = json.loads(scraped_data)
                except json.JSONDecodeError:
                    logger.error(
                        f"⚠️ Invalid JSON response from scraper: {website_link}"
                    )
                    continue  # Skip to the next URL

            if not isinstance(scraped_data, dict):
                logger.warning(f"⚠️ Unexpected data format from scraper: {website_link}")
                continue  # Skip invalid data

            format_data = data_formatter(scraped_data)
            logger.info(f"✅ scrapped data: \n{format_data}")
            # Ensure atomic database transaction

            with transaction.atomic():
                Company.objects.update_or_create(
                    website_link=website_link, defaults=format_data
                )

            logger.info(f"✅ Successfully processed: {website_link}")

        except Exception as e:
            logger.error(f"❌ Error processing {website_link}: {e}", exc_info=True)
            continue  # Skip if scraping fails


async def scrape_with_timeout(url):
    """Run the scraper with a timeout to prevent hanging tasks."""
    try:
        return await asyncio.wait_for(Crawler(url=url).start(), timeout=SCRAPER_TIMEOUT)
    except TimeoutError:
        logger.error(f"⏳ Scraping timeout for: {url}")
        return {}  # Return an empty dictionary to indicate failure
    except Exception as e:
        logger.error(f"❌ Scraper error for {url}: {e}")
        return {}  # Return empty to indicate failure


def data_formatter(scraped_data):
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
        "client_testimonials": listToStr(scraped_data.get("client_testimonials")),
        "oems_working_with": listToStr(scraped_data.get("oems_working_with")),
        "brief_company_profile": scraped_data.get("brief_company_profile"),
        "top_management_details": listToStr(scraped_data.get("top_management_details")),
        "annual_revenue": scraped_data.get("annual_revenue"),
        "average_deal_size": scraped_data.get("average_deal_size"),
        "operating_countries": listToStr(scraped_data.get("operating_countries")),
        "funding_status": scraped_data.get("funding_status"),
        "google_rating": scraped_data.get("google_rating"),
    }
    return format_data
