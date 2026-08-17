import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from schema import AppResearchRecord

# Load environment variables from .env file
load_dotenv()

## Connect directly to Groq's OpenAI-compatible free API
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are an expert AI Product Ops researcher for Composio.
Analyze the given application to evaluate its suitability for building an AI agent toolkit / MCP server.
Output ONLY valid JSON matching this schema:
{
  "app_name": string,
  "category": string,
  "one_line_summary": string,
  "auth_method": "OAuth2" | "API Key" | "Basic" | "Token" | "Other" | "Unknown",
  "access_model": "Self-Serve Free/Trial" | "Paid Plan Required" | "Admin/Partner Gated" | "Contact Sales",
  "api_surface": string,
  "buildability_verdict": "Ready Today" | "Blocked" | "Needs Outreach",
  "blocker_reason": string or null,
  "evidence_url": string
}
"""

def research_app(app_info: dict) -> dict:
    prompt = f"""
    App Name: {app_info['app_name']}
    Category: {app_info['category']}
    Hint URL: {app_info.get('hint_url', '')}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    raw_json = json.loads(response.choices[0].message.content)
    return AppResearchRecord(**raw_json).model_dump()

def run_pipeline(input_file="seed_apps.json", output_file="results_pass1.json", limit=None):
    with open(input_file, "r") as f:
        apps = json.load(f)

    if limit:
        apps = apps[:limit]

    results = []
    for idx, app in enumerate(apps, start=1):
        print(f"[{idx}/{len(apps)}] Researching {app['app_name']}...")
        try:
            record = research_app(app)
            results.append(record)
        except Exception as e:
            print(f"Error on {app['app_name']}: {e}")
        time.sleep(1.2)  # Respect free-tier rate limits

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone! Saved {len(results)} records to {output_file}")

if __name__ == "__main__":
    # Test first on 5 apps to make sure it works
    run_pipeline(limit=None)