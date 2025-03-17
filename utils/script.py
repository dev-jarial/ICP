import asyncio
import json
from typing import List

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()
# Step 1: Create a pruning filter
prune_filter = PruningContentFilter(
    threshold=0.9,
    threshold_type="fixed",
    min_word_threshold=50,
)

# Step 2: Insert it into a Markdown Generator
md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

config = CrawlerRunConfig(
    markdown_generator=md_generator,
    exclude_external_links=True,
    wait_for_images=False,
    image_description_min_word_threshold=False,
    cache_mode=CacheMode.DISABLED,
)

browser_config = BrowserConfig(headless=True)


class CompanyDetails(BaseModel):
    name: str = Field(..., description="The official registered name of the company.")
    email_id: str = Field(
        ...,
        description="The company's official email address (sales, HR, or general contact).",
    )
    mobile_number: str = Field(
        ..., description="The company's primary mobile contact number."
    )
    general_contact_number: str = Field(
        ..., description="The company's general contact number, usually a landline."
    )
    hq_address: str = Field(
        ..., description="The location(s) of the company's headquarters."
    )
    locations_offices: str = Field(
        ..., description="The locations of the company's branch or regional offices."
    )
    key_capabilities: str = Field(
        ..., description="The company's core competencies or areas of expertise."
    )
    products: str = Field(..., description="Products the company develops or offers.")
    industry_types: str = Field(
        ...,
        description="Industries in which the company operates (e.g., Healthcare, IT, Defense).",
    )
    partner_category: str = Field(
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
    top_customer_names: str = Field(
        ..., description="A list of notable or major customers of the company."
    )
    case_studies_available: str = Field(
        ...,
        description="Case studies showcasing real-world applications of the company's solutions.",
    )
    product_brochure: str = Field(
        ..., description="A URL link to the company's product brochure or catalog."
    )
    client_testimonials: str = Field(
        ...,
        description="Statements from clients endorsing the company's products or services.",
    )
    oems_working_with: str = Field(
        ...,
        description="OEMs (Original Equipment Manufacturers) that the company collaborates with.",
    )
    brief_company_profile: str = Field(
        ...,
        description="A concise overview of the company's history, vision, and operations.",
    )
    top_management_details: str = Field(
        ...,
        description="Information about top executives, their roles, and company hierarchy.",
    )
    annual_revenue: float = Field(
        ..., description="The company's annual revenue in USD."
    )
    average_deal_size: float = Field(
        ..., description="The typical value of a business deal closed by the company."
    )
    operating_countries: str = Field(
        ...,
        description="The countries where the company has operations or business presence.",
    )
    funding_status: str = Field(
        ..., description="The current funding stage or financial status of the company."
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
        """,
    }
]


class MeaningFullLinks(BaseModel):
    web_urls: List[str] = Field(
        ...,
        description="web based content render urls",
    )
    doc_urls: List[str] = Field(
        ..., description="those urls, which contains pdf, txt, docs location"
    )


class Crawler:
    def __init__(self, url):
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
            client.beta.chat.completions.parse,
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Your task is to extract key company details from the provided structured data.  Please provide all relevant information information within 1024 tokens
                    Focus on the following aspects:

                    1. **Basic Company Information**:
                    - Name
                    - Email address (official, sales, HR, etc.)
                    - Contact numbers (mobile, general, or support lines)
                    - Physical address (headquarters and additional office locations)

                    2. **Business Operations**:
                    - Categories of services offered
                    - Specific products developed or sold
                    - Industries the company serves

                    3. **Company Experience & Size**:
                    - Years in operation
                    - Number of customers served
                    - Number of employees

                    4. **Client & Market Reputation**:
                    - List of key clients or notable customers
                    - Client testimonials (if available)
                    - Case studies showcasing real-world applications of their solutions

                    5. **Leadership & Management**:
                    - Names and roles of key people in the management team

                    6. **Additional Resources & Ratings**:
                    - Product brochures (if available)
                    - OEM partnerships (Original Equipment Manufacturers the company works with)
                    - Google or industry ratings/reviews (if mentioned)

                    Ensure that the extracted information is **structured, complete, and logically coherent**.
                    Avoid data loss and resolve inconsistencies where necessary. Maintain accuracy while consolidating 
                    information from different sections of the company's website.
                    """,
                },
                {
                    "role": "user",
                    "content": f"Here is the scraped data from the company's website:\n\n{result.markdown}",
                },
            ],
            temperature=0.8,
        )

        scrapped_links = await asyncio.to_thread(
            client.beta.chat.completions.parse,
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Your task is to analyze a list of scraped internal links from a company's website 
            and identify **4-5 most relevant links** that are likely to contain key company details. 
            
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

            From these, extract only 4-5 links that are most relevant for gathering the above company details.
            """,
                },
            ],
            response_format=MeaningFullLinks,
            temperature=0.7,
        )
        content = start_content.choices[0].message.parsed.model_dump()
        self.memory_state.append({"role": "user", "content": f"{content}"})

        sorted_links = scrapped_links.choices[0].message.parsed.model_dump()
        json_sorted_links = json.dumps(sorted_links)

        "Scrape additional pages from extracted meaningful links using multi-threading."
        web_urls = json_sorted_links.get("web_urls", [])

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
            completion.choices[0].message.parsed.model_dump(), indent=4
        )
        return company_details_json

    async def scrape_page(self, link, memory):
        """Scrape a single page using the crawler in a separate thread."""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=link, config=self.crawler_config)

        completion = await asyncio.to_thread(
            self.client.beta.chat.completions.parse,
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """         
            Focus on selecting following meaningful information about:
            
            - **Basic Information**: Name, email, contact numbers, HQ and office locations.
            - **Business Overview**: Key capabilities, products, industry types, and partner categories.
            - **Company Scale & Experience**: Years in operation, number of customers, number of employees.
            - **Clients & Market Presence**: Top customers, case studies, client testimonials, OEM partnerships.
            - **Management & Financials**: Leadership team details, annual revenue, average deal size.
            - **Additional Data**: Operating countries, funding status, Google rating, product brochures.
            """,
                },
                {
                    "role": "user",
                    "content": f"Scraped data from webpage:\n\n{result.markdown}",
                },
            ],
            temperature=0.7,
        )

        extracted_data = completion.choices[0].message.parsed.model_dump()
        memory.append({"role": "user", "content": json.dumps(extracted_data)})
