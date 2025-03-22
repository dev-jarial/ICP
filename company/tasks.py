import asyncio
import json
import logging
from asyncio.exceptions import TimeoutError

from celery import shared_task
from django.db import connections, transaction

from utils.data_format import format
from utils.script import Crawler

from .models import Company

# Set up logging
logger = logging.getLogger(__name__)

# Set an explicit timeout for the scraper (e.g., 150 seconds)
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

            format_data = format(scraped_data)
            logger.info(f"✅ scrapped data: \n{format_data}")
            # Ensure atomic database transaction

            with transaction.atomic():
                Company.objects.update_or_create(
                    name=format_data["name"],
                    website_link=website_link,
                    defaults=format_data,
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
