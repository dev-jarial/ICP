import googleapiclient.discovery

from icp.settings import YOUTUBE_API_KEY

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_search(query: str, n: int = 5):
    youtube = googleapiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY
    )

    request = youtube.search().list(part="snippet", maxResults=n, q=query, type="video")
    response = request.execute()
    return response["items"]


def get_videos_from_query(query: str, n: int = 5) -> list[str]:
    try:
        videos = youtube_search(query, n)
    except:
        get_videos_from_query(query, n)
    print(videos)
    urls = ["https://www.youtube.com/embed/" + v["id"]["videoId"] for v in videos]
    print("============================================")
    print("Query:", query)
    print("URLS:", urls)
    return urls
