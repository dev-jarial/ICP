from serpapi import GoogleSearch

from icp.settings import SERP_API_KEY


def google_rating(name, give=0):
    print(give)
    rating = None
    rating = "Not Available!"
    if give < 3:
        try:
            params = {
                "engine": "google",
                "q": name,
                "api_key": SERP_API_KEY,
            }

            search = GoogleSearch(params)
            serp_results = search.get_dict()
            rating = find_google_rating_recursive(serp_results, "rating")
            # rating = results["knowledge_graph"]["rating"]

        except:
            give += 1
            google_rating(name, give)
    return rating


def find_google_rating_recursive(data, target_key):
    """
    Recursively search for a key in a nested dictionary.
    Returns the value if found, else None.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            # Recurse into nested dict or list
            found = find_google_rating_recursive(value, target_key)
            if found is not None:
                return found

    elif isinstance(data, list):
        for item in data:
            found = find_google_rating_recursive(item, target_key)
            if found is not None:
                return found

    return None
