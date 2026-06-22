import httpx
import os
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": "MUN-Delegate-Assistant/1.0 (educational project) python-httpx"
}


async def scrape_news_api(topic: str) -> list:
    results = []
    try:
        api_key = os.getenv("NEWS_API_KEY")
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic,
            "apiKey": api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5
        }
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for article in data.get("articles", []):
                    title = article.get("title", "")
                    description = article.get("description", "")
                    source = article.get("source", {}).get("name", "News")
                    published = article.get("publishedAt", "")[:10]
                    if title:
                        results.append({
                            "source": source,
                            "title": title,
                            "summary": description or "",
                            "date": published
                        })
    except Exception as e:
        print(f"NewsAPI error: {e}")
    return results


async def scrape_wikipedia(country: str, topic: str) -> str:
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{country} {topic}",
            "format": "json",
            "srlimit": 1
        }
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=HEADERS) as client:
            search_response = await client.get(search_url, params=params)
            search_data = search_response.json()

            if not search_data["query"]["search"]:
                return ""

            page_title = search_data["query"]["search"][0]["title"]
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
            summary_response = await client.get(summary_url)

            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                return summary_data.get("extract", "")
    except Exception as e:
        print(f"Wikipedia scrape error: {e}")
    return ""


async def scrape_reliefweb(topic: str) -> list:
    results = []
    try:
        url = "https://api.reliefweb.int/v2/reports"
        params = {
            "appname": "mun-delegate-assistant",
            "query[value]": topic,
            "limit": 3,
            "fields[include][]": "title",
        }
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=HEADERS) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("data", []):
                    fields = item.get("fields", {})
                    title = fields.get("title", "")
                    if title:
                        results.append({
                            "source": "ReliefWeb",
                            "title": title,
                            "summary": ""
                        })
    except Exception as e:
        print(f"ReliefWeb scrape error: {e}")
    return results


async def scrape_world_bank(country: str) -> dict:
    data = {}
    try:
        country_codes = {
            "india": "IN", "usa": "US", "united states": "US",
            "china": "CN", "russia": "RU", "brazil": "BR",
            "france": "FR", "germany": "DE", "uk": "GB",
            "united kingdom": "GB", "japan": "JP", "canada": "CA",
            "australia": "AU", "pakistan": "PK", "bangladesh": "BD"
        }
        code = country_codes.get(country.lower(), "IN")

        indicators = {
            "NY.GDP.MKTP.CD": "GDP (current US$)",
            "SP.POP.TOTL": "Total Population",
            "NY.GDP.PCAP.CD": "GDP per capita (US$)",
            "SL.UEM.TOTL.ZS": "Unemployment rate (%)"
        }

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            for indicator_code, label in indicators.items():
                url = f"https://api.worldbank.org/v2/country/{code}/indicator/{indicator_code}?format=json&mrv=1"
                response = await client.get(url)
                if response.status_code == 200:
                    result = response.json()
                    if len(result) > 1 and result[1]:
                        value = result[1][0].get("value")
                        year = result[1][0].get("date")
                        if value:
                            data[label] = f"{value:,.0f} ({year})"
    except Exception as e:
        print(f"World Bank error: {e}")
    return data


async def scrape_indian_kanoon(topic: str) -> list:
    results = []
    try:
        from bs4 import BeautifulSoup
        url = f"https://indiankanoon.org/search/?formInput={topic.replace(' ', '+')}&pagenum=0"
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=HEADERS) as client:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                docs = soup.find_all("div", class_="result_title", limit=4)
                for doc in docs:
                    title = doc.get_text(strip=True)
                    if title:
                        results.append({
                            "source": "Indian Kanoon",
                            "title": title
                        })
    except Exception as e:
        print(f"Indian Kanoon error: {e}")
    return results


async def get_all_research(country: str, committee: str, topic: str, mun_type: str) -> dict:
    news = await scrape_news_api(topic)
    wiki = await scrape_wikipedia(country or topic, topic)
    relief = await scrape_reliefweb(topic)
    world_bank = await scrape_world_bank(country) if country else {}
    indian_laws = await scrape_indian_kanoon(topic) if mun_type == "indian" else []

    print(f"Scraped — News: {len(news)}, ReliefWeb: {len(relief)}, Wikipedia: {bool(wiki)}, WorldBank: {len(world_bank)}, IndianKanoon: {len(indian_laws)}")

    return {
        "news": news,
        "wikipedia": wiki,
        "reliefweb": relief,
        "world_bank": world_bank,
        "indian_laws": indian_laws
    }