import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")
TOP_HEADLINES_URL = "https://newsapi.org/v2/top-headlines"
EVERYTHING_URL = "https://newsapi.org/v2/everything"

def fetch_top_headlines(state=None, topic="health"):
    if not API_KEY:
        return [], "NEWSAPI_KEY is not configured."

    if state and state.lower() != "all states (general news)":
        params = {
            "q": f'({state} OR "{state}") AND ({topic})',
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": API_KEY,
            "pageSize": 10
        }
        url = EVERYTHING_URL
    else:
        params = {
            "country": "us",
            "category": topic,
            "apiKey": API_KEY,
            "pageSize": 10
        }
        url = TOP_HEADLINES_URL

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                if articles:
                    return [
                        {
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "url": article.get("url", ""),
                            "publishedAt": article.get("publishedAt", "")
                        }
                        for article in articles
                    ], None
                return [], "No articles found for the selected criteria"

            return [], data.get("message", "Unknown error from NewsAPI")

        return [], f"HTTP {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        return [], "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return [], f"Network error: {str(e)}"
    except Exception as e:
        return [], f"Unexpected error: {str(e)}"