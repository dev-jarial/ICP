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


@shared_task
def process_uploaded_file(valid_urls):
    for website_link in valid_urls:
        process_single_url.delay(website_link)


@shared_task(time_limit=180)
def process_single_url(website_link):
    try:
        connections.close_all()
        logger.info(f"🚀 Processing: {website_link}")

        scraped_data = asyncio.run(scrape_with_timeout(website_link))

        if isinstance(scraped_data, str):
            try:
                scraped_data = json.loads(scraped_data)
            except json.JSONDecodeError:
                logger.error(f"⚠️ Invalid JSON response from scraper: {website_link}")
                return

        if not isinstance(scraped_data, dict):
            logger.warning(f"⚠️ Unexpected data format from scraper: {website_link}")
            return

        format_data = format(scraped_data)
        logger.info(f"✅ scrapped data: \n{format_data}")

        with transaction.atomic():
            Company.objects.update_or_create(
                name=format_data["name"],
                website_link=website_link,
                defaults=format_data,
            )

        logger.info(f"✅ Successfully processed: {website_link}")

    except Exception as e:
        logger.error(f"❌ Error processing {website_link}: {e}", exc_info=True)


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
