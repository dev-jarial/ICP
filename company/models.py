from django.db import models
from pgvector.django import VectorField


class Company(models.Model):
    name = models.CharField(unique=True)  # Unique company name
    email = models.EmailField(blank=True, null=True)
    mobile_number = models.CharField(blank=True, null=True)
    general_contact_number = models.CharField(blank=True, null=True)
    hq_address = models.JSONField(default=list)
    locations = models.JSONField(default=list)  # Store multiple office locations

    key_capabilities = models.JSONField(default=list)
    products = models.JSONField(default=list)  # Store list of products
    industry_types = models.JSONField(default=list)  # Store multiple industries
    partner_category = models.JSONField(default=list)

    number_of_years = models.CharField(blank=True, null=True)  # Years in business
    number_of_customers = models.CharField(blank=True, null=True)
    number_of_employees = models.CharField(blank=True, null=True)

    top_customer_names = models.JSONField(default=list)  # Store list of top customers
    case_studies = models.JSONField(default=list)

    # Store brochure URL instead of boolean
    product_brochure_link = models.URLField(blank=True, null=True)

    client_testimonials = models.JSONField(default=list)
    oems_working_with = models.JSONField(default=list)
    oem_partnership_status = models.JSONField(default=list)
    brief_company_profile = models.JSONField(default=list)

    top_management_details = models.JSONField(default=list)  # Store management details
    annual_revenue = models.CharField(blank=True, null=True)  # Revenue in USD
    average_deal_size = models.CharField(blank=True, null=True)

    operating_countries = models.JSONField(default=list)  # List of countries

    # top_3_competitors_websites = models.JSONField(
    #     default=list
    # )  # Store competitor websites
    funding_status = models.CharField(blank=True, null=True)
    youtube_videos = models.JSONField(default=list)
    google_rating = models.CharField(blank=True, null=True)  # Google rating (e.g., 4.5)

    website_link = models.URLField()

    # Add a Vector field for embeddings
    expertise_embedding = VectorField(dimensions=1536, null=True, default=None)

    class Meta:
        db_table = "company"

    def __str__(self):
        return self.name


class CompanyUpload(models.Model):
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload {self.id} - {self.file.name}"
