import httpx
from bs4 import BeautifulSoup

async def scrape_un_news(topic: str) -> list:
    """Scrape UN News for recent articles on the topic"""
    results = []
    try:
        url = f"https://news.un.org/en/search?q={topic.replace(' ', '+')}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("div", class_="story-content", limit=5)
            for article in articles:
                title = article.find("h3")
                summary = article.find("p")
                if title:
                    results.append({
                        "source": "UN News",
                        "title": title.get_text(strip=True),
                        "summary": summary.get_text(strip=True) if summary else ""
                    })
    except Exception as e:
        print(f"UN News scrape error: {e}")
    return results


async def scrape_wikipedia(country: str, topic: str) -> str:
    """Get Wikipedia summary for country + topic"""
    try:
        query = f"{country} {topic} policy"
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1
        }
        async with httpx.AsyncClient(timeout=10) as client:
            search_response = await client.get(url, params=params)
            search_data = search_response.json()
            if search_data["query"]["search"]:
                page_title = search_data["query"]["search"][0]["title"]
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
                summary_response = await client.get(summary_url)
                summary_data = summary_response.json()
                return summary_data.get("extract", "")
    except Exception as e:
        print(f"Wikipedia scrape error: {e}")
    return ""


async def scrape_reliefweb(topic: str) -> list:
    """Scrape ReliefWeb API for humanitarian context"""
    results = []
    try:
        url = "https://api.reliefweb.int/v1/reports"
        params = {
            "appname": "mun-assistant",
            "query[value]": topic,
            "limit": 3,
            "fields[include][]": ["title", "body-html"]
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            data = response.json()
            for item in data.get("data", []):
                fields = item.get("fields", {})
                results.append({
                    "source": "ReliefWeb",
                    "title": fields.get("title", ""),
                    "summary": fields.get("body-html", "")[:300]
                })
    except Exception as e:
        print(f"ReliefWeb scrape error: {e}")
    return results


async def get_all_research(country: str, committee: str, topic: str) -> dict:
    """Run all scrapers and return combined research"""
    un_news = await scrape_un_news(topic)
    wiki = await scrape_wikipedia(country, topic)
    relief = await scrape_reliefweb(topic)
    return {
        "un_news": un_news,
        "wikipedia": wiki,
        "reliefweb": relief
    }