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

                    You are given a list of companies along with detailed information for each (such as name, capabilities, industries, testimonials, management details, etc.).

                    Your task is to:
                    - Select the **3 most relevant companies** from the provided list **based strictly on the user's query**.
                    - Use **only** the information given. Do **not hallucinate or add any external facts**.
                    - Format the response in **3 separate paragraphs**, one per company.
                    - Each paragraph should:
                        - Start with the company name in **bold**.
                        - Clearly describe why it matches the query using the provided data, including details such as:
                            - Locations (e.g., headquarters, offices)
                            - Key capabilities
                            - Products
                            - Website link(s) in Markdown `[Name](url)` format
                            - CEO, CTO, or other management details if available
                            - Key client information, testimonials, or case studies if available
                    - Do **not** use numbered or bulleted lists.
                    - Do **not** mention companies that are not in the provided list and not relevant to user query.

                    Only return the atmost 3 company using Markdown for styling.
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
