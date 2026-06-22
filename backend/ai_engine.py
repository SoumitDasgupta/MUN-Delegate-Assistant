from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_un_prompt(country: str, committee: str, topic: str, research: dict) -> str:
    news_text = "\n".join([
        f"- [{a.get('date', '')}] {a.get('source', '')}: {a.get('title', '')} — {a.get('summary', '')}"
        for a in research.get("news", [])
    ])
    relief_text = "\n".join([f"- {a.get('title', '')}" for a in research.get("reliefweb", [])])
    wiki_text = research.get("wikipedia", "")[:1000]
    wb = research.get("world_bank", {})
    wb_text = "\n".join([f"- {k}: {v}" for k, v in wb.items()])

    return f"""
You are an expert MUN coach and speechwriter who combines real data with powerful diplomatic language.

Delegate represents: {country}
Committee: {committee}
Agenda: {topic}

--- REAL DATA TO USE AS EVIDENCE ---

Latest News:
{news_text or "No news found."}

UN/Humanitarian Reports:
{relief_text or "No reports found."}

Background:
{wiki_text or "No background found."}

Economic Data (World Bank):
{wb_text or "No economic data found."}

--- YOUR TASK ---

Using the real data above as evidence and context, write a complete, eloquent delegate brief.
Your writing should sound like a seasoned UN diplomat — confident, formal, persuasive.
Weave the real figures and news naturally into the language. Do not just list data points.
Instead, use them to strengthen arguments the way a real delegate would in the chamber.

1. COUNTRY POSITION SUMMARY
   Write 2-3 flowing paragraphs explaining {country}'s stance on {topic}.
   Reference specific real events or figures from the data above to ground the position.

2. POSITION PAPER
   - A strong opening paragraph in formal UN language
   - 3 preambulatory clauses (Recalling / Noting / Deeply concerned by...)
   - 3 operative clauses (Calls upon / Urges / Strongly encourages...)
   Each clause should reference a real fact or event from the data.

3. OPENING SPEECH (90 seconds, ~200 words)
   Write this as if {country}'s delegate is speaking live in the chamber.
   It should be passionate, diplomatic, and reference at least 2 real facts naturally.
   End with a powerful closing line.

4. BLOC ANALYSIS
   Which countries will ally with {country} and which will oppose — and why?
   Write this as strategic advice to the delegate, not a dry list.

5. KEY FACTS & STATISTICS
   5 powerful facts the delegate should have ready.
   Each fact should be grounded in the real data provided above.
   Format: fact + why it matters in this debate.
"""


def build_indian_prompt(politician: str, committee: str, topic: str, research: dict) -> str:
    news_text = "\n".join([
        f"- [{a.get('date', '')}] {a.get('source', '')}: {a.get('title', '')} — {a.get('summary', '')}"
        for a in research.get("news", [])
    ])
    wiki_text = research.get("wikipedia", "")[:1000]
    laws_text = "\n".join([f"- {a.get('title', '')}" for a in research.get("indian_laws", [])])

    return f"""
You are an expert Indian parliamentary MUN coach and speechwriter.
You combine real political data with authentic, passionate Indian political rhetoric.

Delegate represents: {politician}
Committee: {committee}
Agenda: {topic}

--- REAL DATA TO USE AS EVIDENCE ---

Latest News:
{news_text or "No news found."}

Relevant Indian Laws & Judgments:
{laws_text or "No laws found."}

Background:
{wiki_text or "No background found."}

--- YOUR TASK ---

Using the real data above, write a complete delegate brief that sounds authentically like {politician}.
Capture their real speaking style, ideology, and party position.
Weave in real news, laws, and figures naturally — the way a real politician would in Parliament.
Do not just list data. Use it to build arguments, the way {politician} actually speaks.

1. POLITICIAN PROFILE & POSITION
   2-3 paragraphs on who {politician} is, their party, ideology, and stance on {topic}.
   Reference real recent events from the news above.

2. OPENING STATEMENT (2 minutes, ~300 words)
   Write this as if {politician} is speaking live in {committee}.
   Match their actual speaking style — passionate, ideological, authentic.
   Reference at least 2 real facts, laws, or news events naturally in the speech.
   Use Hindi phrases where {politician} typically would.
   End with a powerful line true to their character.

3. KEY ARGUMENTS
   3 strong arguments {politician} would make, each backed by a real fact or law from above.
   Write them as talking points — punchy, quotable, authentic to their voice.

4. POLITICAL BLOC ANALYSIS
   Who will support and oppose {politician}'s position — and why?
   Write as strategic advice, referencing real political dynamics.

5. KEY FACTS & STATISTICS
   5 powerful facts ready to deploy in debate.
   Each grounded in real data above, with why it matters politically.

6. POINTS OF INFORMATION
   3 sharp, tactical questions {politician} might fire at opponents.
   Make them pointed and true to {politician}'s debating style.
"""


async def generate_brief(
    mun_type: str,
    committee: str,
    topic: str,
    country: str = None,
    politician: str = None,
    research: dict = None
) -> str:
    try:
        if mun_type == "un":
            prompt = build_un_prompt(country, committee, topic, research or {})
        else:
            prompt = build_indian_prompt(politician, committee, topic, research or {})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert MUN coach. Always ground your answers in the real data provided. Never make up statistics."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI generation error: {str(e)}"
    
async def generate_analysis(
    mun_type: str,
    committee: str,
    topic: str,
    country: str = None,
    politician: str = None,
    research: dict = None
) -> str:
    research = research or {}

    news_text = "\n".join([
        f"- [{a.get('date', '')}] {a.get('source', '')}: {a.get('title', '')} — {a.get('summary', '')}"
        for a in research.get("news", [])
    ])
    wiki_text = research.get("wikipedia", "")[:1000]
    laws_text = "\n".join([f"- {a.get('title', '')}" for a in research.get("indian_laws", [])])
    wb = research.get("world_bank", {})
    wb_text = "\n".join([f"- {k}: {v}" for k, v in wb.items()])
    relief_text = "\n".join([f"- {a.get('title', '')}" for a in research.get("reliefweb", [])])

    context = f"""
Committee: {committee}
Agenda: {topic}
{"Country: " + country if country else ""}
{"Politician: " + politician if politician else ""}

--- REAL DATA ---
News: {news_text or "None"}
Background: {wiki_text or "None"}
Economic Data: {wb_text or "None"}
{"Laws: " + laws_text if laws_text else ""}
{"Reports: " + relief_text if relief_text else ""}
"""

    prompt = f"""
You are a world-class legal analyst, policy researcher, and MUN expert.

{context}

Your task is to deeply analyse the agenda "{topic}" and identify 6 to 8 distinct, 
significant problems or dimensions within it.

For each problem, you must provide:

PROBLEM [N]: [Give it a sharp, specific title]

DESCRIPTION:
Explain the problem clearly in 2-3 sentences. Be specific, not vague.

TYPE:
State whether this is a Legal / Factual / Logical / Humanitarian / Economic / Political problem.

REAL-WORLD PRECEDENT:
Give a specific real example of where this problem has appeared before in history or current events.
Include: country or institution involved, year, what happened, and the outcome.
Be as specific as possible — names, dates, figures.

CURRENT STATUS:
What is the situation right now? Reference the real news or data provided above if relevant.

PROPOSED SOLUTION:
What is the most credible, practical solution that has been proposed or implemented?
Reference real treaties, laws, resolutions, or policies with their actual names and dates.

DELEGATE RELEVANCE:
In 1-2 sentences, explain why a delegate in {committee} should care about and address this problem.

---

Write all 6-8 problems in this format. Be deeply factual, specific, and grounded.
Use real names, real dates, real figures throughout.
This should read like a policy briefing document, not a generic essay.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a world-class policy analyst and MUN expert. You always cite specific real precedents with dates, figures, and names. You never give vague answers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis error: {str(e)}"

   
async def chat_with_analysis(
    messages: list,
    mun_type: str,
    committee: str,
    topic: str,
    country: str = None,
    politician: str = None,
) -> str:
    try:
        system_prompt = f"""You are an expert MUN coach and policy analyst assistant.
The delegate is preparing for:
- Committee: {committee}
- Agenda: {topic}
- {"Country: " + country if country else "Politician: " + politician}
- Type: {"UN Committee" if mun_type == "un" else "Indian Parliamentary Committee"}

Your job is to:
- Answer questions about the agenda deeply and factually
- Help the delegate refine their arguments
- Suggest better phrasing for speeches or position papers
- Challenge weak arguments and strengthen them
- Provide real precedents, laws, figures when asked
- Give tactical MUN advice when needed

Always be specific, factual, and diplomatically sharp. Never give vague answers."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Chat error: {str(e)}"