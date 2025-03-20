from serpapi import GoogleSearch

from icp.settings import SERP_API_KEY


def google_rating(name):
    params = {
        "engine": "google",
        "q": name,
        "api_key": SERP_API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    rating = results["knowledge_graph"]["rating"]
    return rating
