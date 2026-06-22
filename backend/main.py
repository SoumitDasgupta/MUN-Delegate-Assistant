from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import get_all_research
from ai_engine import generate_brief

app = FastAPI()

# This allows the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This defines what data the frontend will send
class DelegateRequest(BaseModel):
    country: str
    committee: str
    topic: str


@app.get("/")
def root():
    return {"message": "MUN Delegate Assistant API is running!"}


@app.post("/generate")
async def generate(request: DelegateRequest):
    # Step 1: Scrape real-time data
    research = await get_all_research(
        request.country,
        request.committee,
        request.topic
    )

    # Step 2: Send to Gemini AI with scraped data
    brief = await generate_brief(
        request.country,
        request.committee,
        request.topic,
        research
    )

    # Step 3: Return everything to the frontend
    return {
        "brief": brief,
        "research_sources": {
            "un_news_count": len(research["un_news"]),
            "reliefweb_count": len(research["reliefweb"]),
            "wikipedia_found": bool(research["wikipedia"])
        }
    }