from openai import OpenAI
from pgvector.django import CosineDistance

from company.models import Company
from utils.data_format import combine_fields_to_text

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI()


def get_openai_embedding(text):
    response = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def get_company_embedding(company_data: dict):
    combined_text = combine_fields_to_text(company_data)
    company_embeddings = get_openai_embedding(combined_text)

    return company_embeddings


def search_companies(query):
    # Generate the embedding for the combined query
    query_embedding = get_openai_embedding(query)

    # Perform a vector search based on cosine similarity
    companies = Company.objects.annotate(
        similarity=CosineDistance("expertise_embedding", query_embedding)
    ).order_by("similarity")[:10]  # Get the top 5 most similar companies

    return companies
