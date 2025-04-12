from django.forms.models import model_to_dict

from .google_rating import google_rating
from .youtube import get_videos_from_query


def format(scraped_data):
    format_data = {
        "name": scraped_data.get("name"),
        "email": scraped_data.get("email"),
        "mobile_number": scraped_data.get("mobile_number"),
        "general_contact_number": scraped_data.get("general_contact_number"),
        "hq_address": scraped_data.get("hq_address", []),
        "locations": scraped_data.get("locations_offices", []),
        "key_capabilities": scraped_data.get("key_capabilities"),
        "products": scraped_data.get("products"),
        "industry_types": scraped_data.get("industry_types"),
        "partner_category": scraped_data.get("partner_category"),
        "number_of_years": scraped_data.get("number_of_years"),
        "number_of_customers": scraped_data.get("number_of_customers"),
        "number_of_employees": scraped_data.get("number_of_employees"),
        "top_customer_names": scraped_data.get("top_customer_names"),
        "case_studies": scraped_data.get("case_studies"),
        "product_brochure_link": scraped_data.get("product_brochure"),
        "client_testimonials": scraped_data.get("client_testimonials"),
        "oems_working_with": scraped_data.get("oems_working_with"),
        "oem_partnership_status": scraped_data.get("oem_partnership_status"),
        "brief_company_profile": scraped_data.get("brief_company_profile"),
        "top_management_details": scraped_data.get("top_management_details"),
        "annual_revenue": scraped_data.get("annual_revenue"),
        "average_deal_size": scraped_data.get("average_deal_size"),
        "operating_countries": (scraped_data.get("operating_countries")),
        "funding_status": scraped_data.get("funding_status"),
        "youtube_videos": get_videos_from_query(
            query=scraped_data.get("youtube_query"), n=2
        ),
        "google_rating": google_rating(scraped_data.get("name")),
    }
    return format_data


def combine_fields_to_text(company_data: dict):
    # combine relevant fields into a single string
    # Combine relevant fields into a single string
    combined_text = f"Name: {company_data['name']}, "
    combined_text += f"Email: {company_data['email']}, "
    combined_text += f"Mobile Number: {company_data['mobile_number']}, "
    combined_text += (
        f"General Contact Number: {company_data['general_contact_number']}, "
    )
    combined_text += f"HQ Address: {' '.join(company_data.get('hq_address', []))}, "
    combined_text += f"Locations: {' '.join(company_data.get('locations', []))}, "
    combined_text += (
        f"Key Capabilities: {' '.join(company_data.get('key_capabilities', []))}, "
    )
    combined_text += f"Products: {' '.join(company_data.get('products', []))}, "
    combined_text += (
        f"Industry Types: {' '.join(company_data.get('industry_types', []))}, "
    )
    combined_text += (
        f"Partner Category: {' '.join(company_data.get('partner_category', []))}, "
    )
    combined_text += f"Years in Business: {company_data['number_of_years']}, "
    combined_text += f"Number of Customers: {company_data['number_of_customers']}, "
    combined_text += f"Number of Employees: {company_data['number_of_employees']}, "
    combined_text += (
        f"Top Customers: {' '.join(company_data.get('top_customer_names', []))}, "
    )
    combined_text += f"Case Studies: {' '.join(company_data.get('case_studies', []))}, "
    combined_text += f"Product Brochure Link: {company_data['product_brochure_link']}, "
    combined_text += f"Client Testimonials: {' '.join(company_data.get('client_testimonials', []))}, "
    combined_text += (
        f"OEMs Working With: {' '.join(company_data.get('oems_working_with', []))}, "
    )
    combined_text += f"OEM Partnership Status: {' '.join(company_data.get('oem_partnership_status', []))}, "
    combined_text += f"Brief Company Profile: {company_data['brief_company_profile']}, "
    combined_text += f"Top Management Details: {' '.join(company_data.get('top_management_details', []))}, "
    combined_text += f"Annual Revenue: {company_data['annual_revenue']}, "
    combined_text += f"Average Deal Size: {company_data['average_deal_size']}, "
    combined_text += f"Operating Countries: {' '.join(company_data.get('operating_countries', []))}, "
    combined_text += f"Funding Status: {company_data['funding_status']}, "
    combined_text += (
        f"YouTube Videos: {' '.join(company_data.get('youtube_videos', []))}, "
    )
    combined_text += f"Google Rating: {company_data['google_rating']}"

    return combined_text


def format_company(company_queryset):
    companies = [
        model_to_dict(company, exclude=["id", "expertise_embedding"])
        for company in company_queryset
    ]

    combined_companies = []
    for company in companies:
        combined_companies.append(combine_fields_to_text(company))

    return combined_companies
