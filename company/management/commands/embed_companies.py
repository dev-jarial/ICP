# this command is used to embed the company profile, who has not already the embeddings.

from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict

from company.models import Company
from utils.embedding import get_company_embedding


class Command(BaseCommand):
    help = "Generate embeddings for companies without existing embeddings"

    def handle(self, *args, **options):
        companies = Company.objects.filter(expertise_embedding=None)

        if not companies.exists():
            self.stdout.write(
                self.style.SUCCESS("All companies already have the embeddings")
            )
            return

        for company in companies:
            try:
                # Convert company to dict-like structure
                company_dict = model_to_dict(company, exclude=["id"])

                embedding = get_company_embedding(company_dict)
                company.expertise_embedding = embedding
                company.save()

                self.stdout.write(self.style.SUCCESS(f"embedded: {company.name}"))

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error Embedding {company.name}: {str(e)}")
                )
