import asyncio
import json
from typing import List

import validators
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from openai import OpenAI
from pydantic import BaseModel, Field

OPENAI_MODEL = "gpt-4o-mini"

# Step 1: Create a pruning filter
prune_filter = PruningContentFilter(
    # threshold=0.9,
    threshold_type="fixed",
    # min_word_threshold=50,
)

# Step 2: Insert it into a Markdown Generator
md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

config = CrawlerRunConfig(
    markdown_generator=md_generator,
    exclude_external_links=True,
    wait_for_images=False,
    image_description_min_word_threshold=False,
)

browser_config = BrowserConfig(headless=True)


class CompanyDetails(BaseModel):
    name: str = Field(..., description="The official registered name of the company.")
    email: str = Field(
        ...,
        description="The company's official email address (sales, HR, or general contact).",
    )
    mobile_number: str = Field(
        ..., description="The company's primary mobile contact number."
    )
    general_contact_number: str = Field(
        ..., description="The company's general contact number, usually a landline."
    )
    hq_address: list[str] = Field(
        ..., description="The location(s) of the company's headquarters."
    )
    locations_offices: list[str] = Field(
        ..., description="The locations of the company's branch or regional offices."
    )
    key_capabilities: list[str] = Field(
        ..., description="The company's core competencies or areas of expertise."
    )
    products: list[str] = Field(
        ..., description="Products the company develops or offers."
    )
    industry_types: list[str] = Field(
        ...,
        description="Industries in which the company operates (e.g., Healthcare, IT, Defense).",
    )
    partner_category: list[str] = Field(
        ..., description="Categories describing the company's business partnerships."
    )
    number_of_years: str = Field(
        ..., description="The number of years since the company was founded."
    )
    number_of_customers: str = Field(
        ..., description="The total number of customers served by the company."
    )
    number_of_employees: str = Field(
        ..., description="The total number of employees working in the company."
    )
    top_customer_names: list[str] = Field(
        ..., description="A list of notable or major customers of the company."
    )
    case_studies: list[str] = Field(
        ...,
        description="Case studies showcasing real-world applications of the company's solutions.",
    )
    product_brochure: str = Field(
        ..., description="A URL link to the company's product brochure or catalog."
    )
    client_testimonials: list[str] = Field(
        ...,
        description="Statements from clients endorsing the company's products or services.",
    )
    oems_working_with: list[str] = Field(
        ...,
        description="OEMs (Original Equipment Manufacturers) that the company collaborates with.",
    )
    oem_partnership_status: list[str] = Field(
        ...,
        description="OEMs (Original Equipment Manufacturers) that the company's working status with the partners",
    )
    brief_company_profile: str = Field(
        ...,
        description="A concise overview of the company's history, vision, and operations.",
    )
    top_management_details: list[str] = Field(
        ...,
        description="Information about top executives, their roles, and company hierarchy.",
    )
    annual_revenue: float = Field(
        ..., description="The company's annual revenue in USD."
    )
    average_deal_size: float = Field(
        ..., description="The typical value of a business deal closed by the company."
    )
    operating_countries: list[str] = Field(
        ...,
        description="The countries where the company has operations or business presence.",
    )
    funding_status: str = Field(
        ..., description="The current funding stage or financial status of the company."
    )
    youtube_query: str = Field(
        ...,
        description="create  search query for youtube video search, that can result the company related information on the youtube",
    )
    google_rating: float = Field(
        ..., description="The company's rating on Google (out of 5)."
    )


main_messages = [
    {
        "role": "system",
        "content": """You are processing structured data extracted from a company's website. 
        The data is being provided incrementally, one piece at a time, as it is scraped from different pages. 
        
        Your task:
        1. **Merge and consolidate** the incoming data into a single structured representation.
        2. **Ensure completeness** by preserving all relevant details and avoiding data loss.
        3. **Resolve inconsistencies**, such as conflicting values, duplicates, or overlapping information.
        4. **Maintain logical coherence**, ensuring all fields are structured appropriately.
        5. **Do not discard any valuable information**, even if it appears redundant. Instead, intelligently 
        integrate it into the final output.

        Always analyze the context before merging new data to ensure accuracy and consistency.
        Note: field with list type should contains atmost 20 records, atleast can be anything.
        """,
    }
]


class MeaningFullLinks(BaseModel):
    links: List[str] = Field(
        ...,
        description="links those hold meaningful information!",
    )


class Crawler:
    def __init__(self, url):
        self.client = OpenAI()
        self.browser_config = browser_config
        self.config = config
        self.url = url
        self.memory_state = main_messages

    async def start(self):
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=self.url, config=config)
            if result.success:
                internal_links = result.links.get("internal", [])

                for links in internal_links:
                    links.pop("title", None)
                    links.pop("base_domain", None)

        start_content = await asyncio.to_thread(
            self.client.beta.chat.completions.parse,
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """
                                Extract and return the company details. Only include relevant data.
                                the data should be about the following:
                                - "name":  Company name
                                - "email":  Official email address
                                - "contact_numbers":  Phone numbers (mobile and general contact)
                                - "hq_address":  Headquarters address
                                - "locations":  Office locations
                                - "services":  Categories of services provided
                                - "products":  Specific products offered
                                - "industry_types":  Industries the company serves
                                - "experience":
                                    - "years_in_business": Number of years in business
                                    - "number_of_customers": Estimated number of customers
                                    - "number_of_employees": Number of employees
                                - "key_clients":  Notable customers or clients
                                - "client_testimonials":  Extracted testimonials
                                - "top_management":
                                    - "name":  Manager's name
                                    - "role":  Role in company
                                - "case_studies":  Links or references to case studies
                                - "brochure_link": URL to company brochure
                                - "oem_partners":  List of OEM partners
                                - "rating": Overall rating or review score if available
                    """,
                },
                {
                    "role": "user",
                    "content": f"Here is the scraped data from the company's website:\n\n{result.markdown}",
                },
            ],
            response_format=CompanyDetails,
        )

        scrapped_links = await asyncio.to_thread(
            self.client.beta.chat.completions.parse,
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Your task is to analyze a list of scraped internal links from a company's website 
            and identify **5-7 most relevant links** that are likely to contain key company details. 
            
            Focus on selecting links that provide meaningful information about:
            
            - **Basic Information**: Name, email, contact numbers, HQ and office locations.
            - **Business Overview**: Key capabilities, products, industry types, and partner categories.
            - **Company Scale & Experience**: Years in operation, number of customers, number of employees.
            - **Clients & Market Presence**: Top customers, case studies, client testimonials, OEM partnerships.
            - **Management & Financials**: Leadership team details, annual revenue, average deal size.
            - **Additional Data**: Operating countries, funding status, Google rating, product brochures.

            Select only those links that are **most likely** to contain this data and discard irrelevant ones. 
            Ensure your selection is **accurate and meaningful** to maximize information coverage.
            """,
                },
                {
                    "role": "user",
                    "content": f"""Here are the scraped internal links from the company's website:\n\n{str(internal_links)}
            """,
                },
            ],
            response_format=MeaningFullLinks,
        )
        content = start_content.choices[0].message.parsed.model_dump()
        self.memory_state.append({"role": "user", "content": f"{content}"})

        sorted_links = scrapped_links.choices[0].message.parsed.model_dump()

        "Scrape additional pages from extracted meaningful links using multi-threading."
        web_urls = sorted_links["links"]

        # Use asyncio.gather to run multiple scrape tasks in parallel
        await asyncio.gather(
            *[self.scrape_page(link, self.memory_state) for link in web_urls]
        )
        # Consolidate scraped data using OpenAI
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=self.memory_state,
            response_format=CompanyDetails,
        )

        company_details_json = json.dumps(
            completion.choices[0].message.parsed.model_dump()
        )
        return company_details_json

    async def scrape_page(self, link, memory):
        """Scrape a single page using the crawler in a separate thread."""

        if validators.url(link):
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(url=link, config=self.config)

            if len(result.markdown) > 1000:
                completion = await asyncio.to_thread(
                    self.client.beta.chat.completions.parse,
                    model=OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": """         
                                Extract and return the company details. Only include relevant data.
                                the data should be about the following:
                                - "name":  Company name
                                - "email":  Official email address
                                - "contact_numbers":  Phone numbers (mobile and general contact)
                                - "hq_address":  Headquarters address
                                - "locations":  Office locations
                                - "services":  Categories of services provided
                                - "products":  Specific products offered
                                - "industry_types":  Industries the company serves
                                - "experience":
                                    - "years_in_business": Number of years in business
                                    - "number_of_customers": Estimated number of customers
                                    - "number_of_employees": Number of employees
                                - "key_clients":  Notable customers or clients
                                - "client_testimonials":  Extracted testimonials
                                - "top_management":
                                    - "name":  Manager's name
                                    - "role":  Role in company
                                - "case_studies":  Links or references to case studies
                                - "brochure_link": URL to company brochure
                                - "oem_partners":  List of OEM partners
                                - "rating": Overall rating or review score if available
                    """,
                        },
                        {
                            "role": "user",
                            "content": f"Scraped data from webpage:\n\n{result.markdown}",
                        },
                    ],
                    response_format=CompanyDetails,
                )
                content = completion.choices[0].message.parsed.model_dump()

                memory.append({"role": "user", "content": f"{content}"})
