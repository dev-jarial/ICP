from .google_rating import google_rating
from .list_str import listToStr
from .youtube import get_videos_from_query


def format(scraped_data):
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
        "oem_partnership_status": listToStr(scraped_data.get("oem_partnership_status")),
        "brief_company_profile": scraped_data.get("brief_company_profile"),
        "top_management_details": listToStr(scraped_data.get("top_management_details")),
        "annual_revenue": scraped_data.get("annual_revenue"),
        "average_deal_size": scraped_data.get("average_deal_size"),
        "operating_countries": listToStr(scraped_data.get("operating_countries")),
        "funding_status": scraped_data.get("funding_status"),
        "youtube_videos": listToStr(
            get_videos_from_query(query=scraped_data.get("youtube_query"), n=2)
        ),
        "google_rating": google_rating(scraped_data.get("name")),
    }
    return format_data
