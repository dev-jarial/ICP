from openai import OpenAI

client = OpenAI()
OPENAI_MODEL = "gpt-4o-mini"


def companies_analyze(companyies_list, query):
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
                    You are a helpful assistant.

                    You are given a list of companies along with detailed information for each (such as name, capabilities, industries, testimonials, and more).

                    Your task is to:
                    - Select the **3 most relevant companies** from the provided list **based strictly on the user's query**.
                    - Use **only** the information given. Do **not hallucinate or add any external facts**.
                    - Format the response in **3 separate paragraphs**, one per company.
                    - Each paragraph should:
                        - Start with the company name in bold.
                        - Clearly describe why it matches the query using the provided data (capabilities, industries, certifications, etc.).
                        - Include a link to the company website if available (Markdown `[Name](url)` format).
                        - Include some detailing like locations (where company or offices present), key capabilities, Industry types and case studies.
                    - Do **not use numbered or bulleted lists**.
                    - Do **not mention companies that are not in the provided list**.

                    Only return the 3 structured company paragraphs using Markdown for styling.
            """.strip(),
            },
            {
                "role": "user",
                "content": f"""
                    Here are the company details:

                    {companyies_list}

                    User query:
                    {query}
            """.strip(),
            },
            {
                "role": "user",
                "content": f"""
                    User query:
                    {query}
            """.strip(),
            },
        ],
    )

    content = response.choices[0].message.content
    return content
