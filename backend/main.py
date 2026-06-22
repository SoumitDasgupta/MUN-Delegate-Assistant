from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from scraper import get_all_research
from ai_engine import generate_brief, generate_analysis, chat_with_analysis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DelegateRequest(BaseModel):
    mun_type: str
    committee: str
    topic: str
    country: Optional[str] = None
    politician: Optional[str] = None


@app.get("/")
def root():
    return {"message": "MUN Delegate Assistant API is running!"}


@app.post("/generate")
async def generate(request: DelegateRequest):
    # Step 1: Scrape real-time data
    research = await get_all_research(
        country=request.country or request.politician or "",
        committee=request.committee,
        topic=request.topic,
        mun_type=request.mun_type
    )

    # Step 2: Generate brief with real data
    brief = await generate_brief(
        mun_type=request.mun_type,
        committee=request.committee,
        topic=request.topic,
        country=request.country,
        politician=request.politician,
        research=research
    )

    return {
        "brief": brief,
        "research_sources": {
            "news_count": len(research["news"]),
            "reliefweb_count": len(research["reliefweb"]),
            "wikipedia_found": bool(research["wikipedia"]),
            "world_bank_found": bool(research["world_bank"]),
            "indian_laws_found": len(research["indian_laws"])
        }
    }

@app.post("/analyse")
async def analyse(request: DelegateRequest):
    research = await get_all_research(
        country=request.country or request.politician or "",
        committee=request.committee,
        topic=request.topic,
        mun_type=request.mun_type
    )

    analysis = await generate_analysis(
        mun_type=request.mun_type,
        committee=request.committee,
        topic=request.topic,
        country=request.country,
        politician=request.politician,
        research=research
    )

    return {"analysis": analysis}

class ChatRequest(BaseModel):
    mun_type: str
    committee: str
    topic: str
    country: Optional[str] = None
    politician: Optional[str] = None
    messages: list



@app.post("/chat")
async def chat(request: ChatRequest):
    reply = await chat_with_analysis(
        messages=request.messages,
        mun_type=request.mun_type,
        committee=request.committee,
        topic=request.topic,
        country=request.country,
        politician=request.politician,
    )
    return {"reply": reply}