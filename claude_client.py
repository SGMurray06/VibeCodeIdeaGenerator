import json
import os
import random
import re

from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5-20251001"


CREATIVE_CONSTRAINTS = [
    "One idea should solve a real frustration the founders likely experience themselves.",
    "One idea should target a specific professional niche with a clear willingness to pay.",
    "One idea should improve an existing workflow that people currently solve with spreadsheets or manual processes.",
    "One idea should be something a small team could realistically launch and get first users within 30 days.",
    "One idea should address a gap in tools available to small businesses or freelancers.",
]


async def generate_ideas(euty_experience: str, simon_experience: str) -> list[dict]:
    """Generate 3 app ideas based on combined experience."""
    constraint = random.choice(CREATIVE_CONSTRAINTS)

    response = await client.messages.create(
        model=MODEL,
        max_tokens=1500,
        temperature=0.8,
        system="You are a practical product strategist who spots real-world opportunities where two people's combined skills can solve genuine problems. You focus on ideas that are buildable by a two-person team, have clear target users, and address real pain points. You prefer clever over flashy, and useful over novel. You always respond with valid JSON.",
        messages=[
            {
                "role": "user",
                "content": f"""Two people want to build an app together. Here are their backgrounds:

**Euty's Experience & Current Interests:**
{euty_experience}

**Simon's Experience & Current Interests:**
{simon_experience}

Suggest exactly 3 practical, buildable app ideas they could vibe-code together. Each idea should:
- Leverage both of their strengths
- Solve a real problem for a specific audience
- Be realistic for a two-person team to build and launch
- Have a clear path to finding first users

{constraint}

Respond with a JSON array of exactly 3 objects, each with:
- "title": a catchy, concise app name (2-4 words)
- "summary": a 2-3 sentence description of what the app does, who it's for, and why this team is uniquely positioned to build it
- "why_exciting": one punchy sentence explaining what makes this idea a smart bet

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
        max_tokens=3000,
        system="You're a technical co-founder who's shipped multiple products. You give honest, practical advice — no consultant-speak. You tailor recommendations to what the team actually knows and can build. Format your response with clear markdown headers and bullet points.",
        messages=[
            {
                "role": "user",
                "content": f"""Analyze the following app idea in depth. This app would be built by two people:

**Euty's Experience & Skills:** {euty_experience}
**Simon's Experience & Skills:** {simon_experience}

**App Idea:** {title}
**Description:** {summary}

Provide a practical deep-dive covering these four areas:

## Build Requirements
- Tech stack recommendation based on what this team actually knows (don't suggest tools they'd have to learn from scratch unless essential)
- MVP features — the smallest version that delivers real value (be ruthless about cutting scope)
- Main technical risks and how to mitigate them
- Estimated costs for the first 6 months (hosting, APIs, third-party services, domains — give specific dollar ranges)

## First Weekend Sprint
- What could they realistically build in 2 days to validate this idea
- One specific experiment to test whether people actually want this before building the full thing

## Route to Market
- Who exactly are the first users (be specific — not "small businesses" but "freelance designers who invoice more than 5 clients a month")
- What's this team's unfair advantage over anyone else who could build this
- Pricing model with specific price points and why
- How to get the first 10 paying users (concrete steps, not generic advice)

## Growth Playbook
- Top 2 acquisition channels for this specific product and why they'll work
- One growth loop built into the product (how does one user naturally bring another)
- The 3 metrics that matter most (ignore vanity metrics)
- 30/60/90 day milestones — what does success look like at each stage

Be direct and specific. Skip the caveats and disclaimers. Tell them what to do.""",
            }
        ],
    )

    return response.content[0].text
