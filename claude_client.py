import json
import os
import re

from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5-20251001"


async def generate_ideas(euty_experience: str, simon_experience: str) -> list[dict]:
    """Generate 3 app ideas based on combined experience."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="You are a creative startup advisor. You specialize in identifying app and software ideas that combine the strengths of a two-person team. You always respond with valid JSON.",
        messages=[
            {
                "role": "user",
                "content": f"""Two people want to build an app together. Here are their backgrounds:

**Euty's Experience:**
{euty_experience}

**Simon's Experience:**
{simon_experience}

Based on their combined skills and experience, suggest exactly 3 tailored app ideas they could vibe-code together. Each idea should leverage both of their strengths.

Respond with a JSON array of exactly 3 objects, each with:
- "title": a catchy, concise app name (2-4 words)
- "summary": a 2-3 sentence description of what the app does, who it's for, and why this team is uniquely positioned to build it

Respond ONLY with the JSON array, no other text.""",
            }
        ],
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        ideas = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: extract first JSON array from response
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            ideas = json.loads(match.group())
        else:
            raise ValueError("Could not parse ideas from Claude response")

    return ideas


async def generate_deep_dive(
    title: str, summary: str, euty_experience: str, simon_experience: str
) -> str:
    """Generate a deep-dive analysis for an app idea."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system="You are a senior product strategist and technical advisor. You provide detailed, actionable analysis for app ideas. Format your response with clear markdown headers and bullet points.",
        messages=[
            {
                "role": "user",
                "content": f"""Analyze the following app idea in depth. This app would be built by two people:

**Euty's Experience:** {euty_experience}
**Simon's Experience:** {simon_experience}

**App Idea:** {title}
**Description:** {summary}

Provide a comprehensive deep-dive covering these three areas:

## Build Requirements
- Core technical stack recommendation
- Key features for an MVP (minimum viable product)
- Estimated development timeline for two people
- Main technical challenges and how to address them

## Route to Market
- Target audience and market size
- Competitive landscape and differentiation
- Pricing model suggestions
- Launch strategy (beta, soft launch, etc.)

## Adoption Strategy
- User acquisition channels
- Growth tactics specific to this product
- Key metrics to track
- First 90-day milestones

Be specific and actionable. Tailor all advice to the team's combined experience.""",
            }
        ],
    )

    return response.content[0].text
