from serpapi import GoogleSearch

from icp.settings import SERP_API_KEY


def google_rating(name, give=0):
    print(give)
    rating = None
    if not give < 3:
        rating = "Not able to fetch!"
    else:
        try:
            params = {
                "engine": "google",
                "q": name,
                "api_key": SERP_API_KEY,
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            print(results["knowledge_graph"])
            rating = results["knowledge_graph"]["rating"]

        except:
            give += 1
            google_rating(name, give)
    return rating
