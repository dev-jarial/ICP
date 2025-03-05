import asyncio
import json

import validators
from django.shortcuts import render

from utils.web_crawler import main

from .forms import CompanyForm
from .models import Company

# from your_scraping_module import scrape_company_data  # Your custom scraping logic


def company_form_view(request):
    scraped_data = None  # Initialize
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
                    scraped_data = asyncio.run(main(url=website_link))

                    # Ensure scraped_data is a dictionary
                    if isinstance(scraped_data, str):
                        scraped_data = json.loads(scraped_data)

                    print(
                        "Final Data Sent to Template:", scraped_data
                    )  # Debugging output

                except Exception as e:
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
