import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from schema import AppResearchRecord

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are an expert AI Product Ops researcher for Composio.
Analyze the given application to evaluate its suitability for building an AI agent toolkit / MCP server.
You must return JSON using exact snake_case keys matching this format:
{
  "app_name": "string",
  "category": "string",
  "one_line_summary": "string",
  "auth_method": "OAuth2" | "API Key" | "Basic" | "Token" | "Other" | "Unknown",
  "access_model": "Self-Serve Free/Trial" | "Paid Plan Required" | "Admin/Partner Gated" | "Contact Sales" | "Unknown",
  "api_surface": "string",
  "buildability_verdict": "Ready Today" | "Blocked" | "Needs Outreach",
  "blocker_reason": "string or null",
  "evidence_url": "string"
}
"""

def normalize_keys(d: dict) -> dict:
    mapping = {
        "appName": "app_name",
        "oneLineSummary": "one_line_summary",
        "authMethod": "auth_method",
        "accessModel": "access_model",
        "apiSurface": "api_surface",
        "buildabilityVerdict": "buildability_verdict",
        "blockerReason": "blocker_reason",
        "evidenceUrl": "evidence_url"
    }
    return {mapping.get(k, k): v for k, v in d.items()}

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
    cleaned = normalize_keys(raw_json)
    return AppResearchRecord(**cleaned).model_dump()

def fix_dataset():
    with open("seed_apps.json", "r") as f:
        all_seed_apps = json.load(f)

    with open("results_pass1.json", "r") as f:
        existing_results = json.load(f)

    existing_names = {r["app_name"].strip().lower() for r in existing_results}
    
    missing_apps = [
        app for app in all_seed_apps 
        if app["app_name"].strip().lower() not in existing_names
    ]

    print(f"Missing apps to fetch: {[a['app_name'] for a in missing_apps]}\n")

    for app in missing_apps:
        print(f"Fetching {app['app_name']}...")
        try:
            record = research_app(app)
            existing_results.append(record)
            print(f"  -> Added {app['app_name']}")
        except Exception as e:
            print(f"  -> Error on {app['app_name']}: {e}")
        time.sleep(1.0)

    with open("results_pass1.json", "w") as f:
        json.dump(existing_results, f, indent=2)

    print(f"\nFinished! Total records in results_pass1.json: {len(existing_results)}")

if __name__ == "__main__":
    fix_dataset()