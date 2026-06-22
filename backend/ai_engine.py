from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_prompt(country: str, committee: str, topic: str, research: dict) -> str:
    """Build a detailed prompt using scraped research data"""

    un_news_text = ""
    for article in research.get("un_news", []):
        un_news_text += f"- {article['title']}: {article['summary']}\n"

    reliefweb_text = ""
    for item in research.get("reliefweb", []):
        reliefweb_text += f"- {item['title']}: {item['summary']}\n"

    wikipedia_text = research.get("wikipedia", "No Wikipedia data found.")

    prompt = f"""
You are an expert MUN (Model United Nations) coach helping a delegate prepare for a conference.

The delegate is representing: {country}
Committee: {committee}
Topic: {topic}

Here is real-time research gathered from the internet:

--- UN NEWS (Latest Articles) ---
{un_news_text if un_news_text else "No recent UN news found."}

--- RELIEFWEB (Humanitarian Context) ---
{reliefweb_text if reliefweb_text else "No ReliefWeb data found."}

--- WIKIPEDIA (Background) ---
{wikipedia_text}

Based on this real-time research, please provide:

1. COUNTRY POSITION SUMMARY
   - What is {country}'s likely stance on {topic}?
   - Key interests and concerns

2. POSITION PAPER (ready to submit)
   - Opening paragraph
   - 3 preambulatory clauses
   - 3 operative clauses

3. OPENING SPEECH (90 seconds, formal UN language)

4. BLOC ANALYSIS
   - Which countries will likely ally with {country}?
   - Which countries will likely oppose?
   - Why?

5. KEY FACTS & STATISTICS
   - 5 important facts the delegate should know

Keep the tone formal, diplomatic, and accurate to real UN proceedings.
"""
    return prompt


async def generate_brief(country: str, committee: str, topic: str, research: dict) -> str:
    """Generate full MUN brief using Gemini"""
    try:
        prompt = build_prompt(country, committee, topic, research)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI generation error: {str(e)}"