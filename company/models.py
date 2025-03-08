from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Unique company name
    email = models.EmailField(blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    general_contact_number = models.CharField(max_length=20, blank=True, null=True)
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
    case_studies_available = models.JSONField(default=list)

    # Store brochure URL instead of boolean
    product_brochure_link = models.URLField(blank=True, null=True)

    client_testimonials = models.JSONField(default=list)
    oems_working_with = models.JSONField(default=list)  # Store list of OEM partners
    brief_company_profile = models.TextField(blank=True, null=True)

    top_management_details = models.JSONField(default=list)  # Store management details
    annual_revenue = models.CharField(blank=True, null=True)  # Revenue in USD
    average_deal_size = models.CharField(blank=True, null=True)

    operating_countries = models.JSONField(default=list)  # List of countries

    # top_3_competitors_websites = models.JSONField(
    #     default=list
    # )  # Store competitor websites
    funding_status = models.CharField(max_length=255, blank=True, null=True)
    google_rating = models.CharField(blank=True, null=True)  # Google rating (e.g., 4.5)

    website_link = models.URLField()

    class Meta:
        db_table = "company"

    def __str__(self):
        return self.name


class CompanyUpload(models.Model):
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload {self.id} - {self.file.name}"
