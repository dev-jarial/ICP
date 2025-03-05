from django.shortcuts import render, redirect
from .forms import CompanyDetailsForm
from .models import CompanyDetails
# from your_scraping_module import scrape_company_data  # Your custom scraping logic

def company_form_view(request):
    if request.method == 'POST':
        form = CompanyDetailsForm(request.POST)
        if form.is_valid():
            website_link = form.cleaned_data['website_link']
            
            # Check if company already exists
            existing_company = CompanyDetails.objects.filter(website_link=website_link).first()
            if existing_company:
                # Update existing record or return message
                return render(request, 'company/company_form.html', {
                    'form': form, 
                    'message': 'Company already exists in database.'
                })
            
            # Scrape company data
            # try:
            #     company_data = scrape_company_data(website_link)
                
            #     # Create new company record
            #     new_company = CompanyDetails(
            #         website_link=website_link,
            #         **company_data  # Unpack scraped data
            #     )
            #     new_company.save()
                
            #     return render(request, 'companies/company_form.html', {
            #         'form': form, 
            #         'message': 'Company details successfully added!'
            #     })
            
            # except Exception as e:
            #     return render(request, 'companies/company_form.html', {
            #         'form': form, 
            #         'error': f'Scraping failed: {str(e)}'
            #     })
    
    form = CompanyDetailsForm()
    return render(request, 'company/company_form.html', {'form': form})
