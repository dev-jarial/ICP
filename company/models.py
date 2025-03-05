from django.db import models
from django.core.validators import FileExtensionValidator

class CompanyDetails(models.Model):
    # Basic Company Information
    company_name = models.CharField(max_length=255, unique=True)
    email_id = models.EmailField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    general_contact_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    locations = models.TextField(blank=True, null=True)  # Multiple locations can be comma-separated
    
    # Classification
    categories = models.CharField(max_length=255, blank=True, null=True)
    industry_types = models.CharField(max_length=255, blank=True, null=True)
    
    # Company Performance
    years_in_business = models.IntegerField(blank=True, null=True)
    number_of_customers = models.IntegerField(default=0)
    number_of_employees = models.IntegerField(default=0)
    
    # Additional Details
    customer_names = models.TextField(blank=True, null=True)
    case_studies = models.TextField(blank=True, null=True)
    
    # File Uploads
    product_brochure = models.FileField(
        upload_to='brochures/', 
        blank=True, 
        null=True, 
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])]
    )
    client_testimonials = models.TextField(blank=True, null=True)
    
    # Company Credentials
    oems = models.TextField(blank=True, null=True)
    company_profile = models.FileField(
        upload_to='profiles/', 
        blank=True, 
        null=True, 
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])]
    )
    management_details = models.TextField(blank=True, null=True)
    
    # External Ratings
    google_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        blank=True, 
        null=True
    )
    
    # Website Scraping Reference
    website_link = models.URLField(unique=True)
    
    def __str__(self):
        return self.company_name
