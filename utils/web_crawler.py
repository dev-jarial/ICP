import asyncio
import json
from typing import List

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()
# Step 1: Create a pruning filter
prune_filter = PruningContentFilter(
    # Lower → more content retained, higher → more content pruned
    threshold=0.9,
    # "fixed" or "dynamic"
    threshold_type="fixed",
    # Ignore nodes with <5 words
    min_word_threshold=5,
)

# Step 2: Insert it into a Markdown Generator
md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

config = CrawlerRunConfig(
    exclude_external_links=True,
    wait_for_images=False,
    image_description_min_word_threshold=False,
)

browser_config = BrowserConfig(headless=False)

main_messages = [
    {
        "role": "system",
        "content": """I am providing you the structured data that I have extracted through the company's 
        website. The data I am sharing you one by one, as it is scrapped from each page. You have to merge 
        these data into one. Analyze these data and never miss any valuable information.""",
    }
]


class CompanyDetails(BaseModel):
    company_name: str = Field(..., description="the name of the company.")
    email_id: str = Field(
        ..., description="officla or sales or hr emmail of the company."
    )
    mobile_number: str = Field(..., description="mobile number of the company.")
    general_contact_number: str = Field(
        ...,
        description="general contact number of the company, usually telephone number.",
    )
    hq_address: str = Field(
        ..., description="where company's headquarters are located."
    )
    locations_offices: list[str] = Field(
        ..., description="where are the other locations of company's offices."
    )
    key_capabilities: list[str] = Field(
        ...,
        description="key capabilities, in which areas or sectors company actually works",
    )
    products: list[str] = Field(..., description="products that company offer or build")
    industry_types: list[str] = Field(
        ...,
        description="""industries where company actually works, like healthcare, education, Computer and Networking, 
        Software and Development, defence, agriculture etc""",
    )

    partner_category: list[str] = Field(
        ...,
        description="List of the categories, where company's partner actually work.",
    )

    number_of_years: str = Field(..., description="how old is company")
    number_of_customers: str = Field(..., description="how many customers company have")
    number_of_employees: str = Field(
        ..., description="how many employees work in the company"
    )
    top_customer_names: list[str] = Field(
        ...,
        description="list of top customers names",
    )
    case_studies_available: list[str] = Field(
        ...,
        description="case studies that showcase the company's work by solving the real life issues",
    )
    product_brochure: str = Field(
        ..., description="url link about the company's brochure"
    )
    client_testimonials: list[str] = Field(
        ...,
        description="statements from customers that praise a business, product, or service offered by the company",
    )
    oems_working_with: list[str] = Field(
        ...,
        description="Services or products of the company for other companies to sell under their own brand",
    )
    brief_company_profile: str = Field(..., description="description of the company")
    top_management_details: list[str] = Field(
        ...,
        description="details about the top roles, responsibilities, hierarchy within the organization",
    )
    annual_revenue: float = Field(..., description="Annual revenue of the company")
    average_deal_size: float = Field(
        ..., description="Average cost deal size company make."
    )
    operating_countries: list[str] = Field(
        ..., description="Company operating in which countries"
    )
    funding_status: str = Field(
        ..., description="What the funding status of the company"
    )
    google_rating: str = Field(..., description="Rating out of 5, like: 3, 4.5, 2.")


class MeaningFullLinks(BaseModel):
    web_urls: List[str] = Field(
        ...,
        description="web based content render urls",
    )
    doc_urls: List[str] = Field(
        ..., description="those urls, which contains pdf, txt, docs location"
    )


async def home_scrape(url):
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=config)

        if result.success:
            internal_links = result.links.get("internal", [])

            for links in internal_links:
                links.pop("title", None)
                links.pop("base_domain", None)
    completion = await asyncio.to_thread(
        client.beta.chat.completions.parse,
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """Please extract the relevant details about the company from the following information. 
        Focus on the company's name, email address, contact number, and physical address. Identify the 
        various locations where the company has offices. List the categories of services offered, along with 
        any specific products the company provides. Also, extract the types of industries the company serves.
          Include details about the company’s experience, such as how long it has been in business, the 
          number of customers it serves, and the number of employees it has. Make sure to mention any key 
          clients or notable customers. If there are any client testimonials, include them as well. Identify
            the key people in the management team and list their roles. Lastly, check for any case studies, 
            brochures, or OEM details, and include a rating or review if available.""",
            },
            {
                "role": "user",
                "content": f"Here is scrapped data of the companies web site: \n\n{result.markdown.fit_markdown}",
            },
        ],
        response_format=CompanyDetails,
        temperature=0.8,
    )
    scrapped_links = await asyncio.to_thread(
        client.beta.chat.completions.parse,
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract the links those may contain the meaningful information about the company",
            },
            {
                "role": "user",
                "content": f"""Here is scrapped links from the companies web site: \n\n{str(internal_links)}. 
                From these links, I want only few links, like 4-5 links. Those can provide these information 
                company_name
                email_id
                mobile_number
                general_contact_number
                hq_address
                locations_offices
                key_capabilities
                products
                industry_types
                partner_category
                number_of_years
                number_of_customers
                number_of_employees
                top_customer_names
                case_studies_available
                product_brochure
                client_testimonials
                oems_working_with
                brief_company_profile
                top_management_details
                annual_revenue
                average_deal_size
                operating_countries
                funding_status
                google_rating""",
            },
        ],
        response_format=MeaningFullLinks,
        temperature=0.7,
    )

    content = completion.choices[0].message.parsed.model_dump()

    main_messages.append({"role": "user", "content": f"{content}"})

    sorted_links = scrapped_links.choices[0].message.parsed.model_dump()
    json_sorted_links = json.dumps(sorted_links)

    return json_sorted_links


async def mini_links_scrape(links):
    async with AsyncWebCrawler(config=browser_config) as crawler:
        web_urls = links.get("web_urls")
        # doc_urls = links.get("doc_urls")

        for link in web_urls:
            result = await crawler.arun(url=link, config=config)
            completion = await asyncio.to_thread(
                client.beta.chat.completions.parse,
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """Please extract the relevant details about the company from the following 
                        information. Focus on the company's name, email address, contact number, and physical address. Identify the 
                        various locations where the company has offices. List the categories of services offered, along with 
                        any specific products the company provides. Also, extract the types of industries the company serves.
                        Include details about the company’s experience, such as how long it has been in business, the 
                        number of customers it serves, and the number of employees it has. Make sure to mention any key 
                        clients or notable customers. If there are any client testimonials, include them as well. Identify
                        the key people in the management team and list their roles. Lastly, check for any case studies, 
                        brochures, or OEM details, and include a rating or review if available.""",
                    },
                    {
                        "role": "user",
                        "content": f"Here is scrapped data of the companies web site: \n\n{result.markdown.fit_markdown}",
                    },
                ],
                response_format=CompanyDetails,
                temperature=0.6,
            )
            content = completion.choices[0].message.parsed.model_dump()
            main_messages.append({"role": "user", "content": f"{content}"})

        # for link in doc_urls:
        #     result = await crawler.arun(url=link, config=config)
        #     completion = await asyncio.to_thread(
        #         client.chat.completions.create,
        #         model="gpt-4o-mini",
        #         messages=[
        #             {
        #                 "role": "system",
        #                 "content": """On the basis given content, you have to extract the only
        #                 meaningful information about the company. The content provided you is the scrapped content
        #                 from the company's site and in markdown format""",
        #             },
        #             {
        #                 "role": "user",
        #                 "content": f"Here is scrapped data of the companies web site: \n\n{result.markdown_v2.raw_markdown}",
        #             },
        #         ],
        #         max_tokens=500,
        #     )
        #     content = completion.choices[0].message.content
        #     main_messages.append({"role": "user", "content": f"{content}"})

        return True


async def main(url: str):
    related_links = await home_scrape(url=url)
    url_scraped_true = await mini_links_scrape(links=json.loads(related_links))
    if url_scraped_true:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=main_messages,
            response_format=CompanyDetails,
            temperature=0.5,
        )
        event = completion.choices[0].message.parsed.model_dump()
        company_details_json = json.dumps(event, indent=4)
        return company_details_json


if __name__ == "__main__":
    web_site = "https://onmeridian.com"
    result = asyncio.run(main=main(url=web_site))
