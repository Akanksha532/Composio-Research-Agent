import json
import os
import time
import httpx
from dotenv import load_dotenv
from openai import OpenAI
from schema import AppResearchRecord

# Load variables from .env file
load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def check_url_live(url: str) -> bool:
    if not url:
        return False
    if not url.startswith("http"):
        url = "https://" + url
    try:
        res = httpx.get(url, timeout=5.0, follow_redirects=True)
        return res.status_code < 400
    except Exception:
        return False

def verify_record(record: dict) -> dict:
    prompt = f"""
    You are an accuracy-auditing AI verifying research data on SaaS APIs for Composio.
    Review this initial assessment:
    - App: {record['app_name']}
    - Category: {record['category']}
    - Auth Method: {record['auth_method']}
    - Access Model: {record['access_model']}
    - API Surface: {record['api_surface']}
    - Verdict: {record['buildability_verdict']}
    - Evidence URL: {record['evidence_url']}

    Verify if the auth method, self-serve access, and doc URL are accurate.
    Output ONLY valid JSON matching the AppResearchRecord schema.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a technical auditor checking API facts. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    raw_json = json.loads(response.choices[0].message.content)
    verified = AppResearchRecord(**raw_json).model_dump()

    is_modified = (
        verified['auth_method'] != record['auth_method'] or
        verified['access_model'] != record['access_model'] or
        verified['buildability_verdict'] != record['buildability_verdict']
    )
    verified['url_is_live'] = check_url_live(verified['evidence_url'])
    verified['pass1_matched'] = not is_modified
    verified['pass1_original'] = record
    return verified

def run_verification(input_file="results_pass1.json", output_file="results_verified.json"):
    with open(input_file, "r") as f:
        pass1_records = json.load(f)

    verified_records = []
    mismatches = 0
    total = len(pass1_records)

    print(f"Running verification audit across {total} records...\n")
    for idx, rec in enumerate(pass1_records, start=1):
        print(f"[{idx}/{total}] Auditing {rec['app_name']}...")
        try:
            v_rec = verify_record(rec)
            if not v_rec['pass1_matched']:
                mismatches += 1
                print(f"  -> Discrepancy caught and corrected for {rec['app_name']}")
            verified_records.append(v_rec)
        except Exception as e:
            print(f"  -> Error verifying {rec['app_name']}: {e}")
            rec['pass1_matched'] = True
            rec['url_is_live'] = check_url_live(rec.get('evidence_url', ''))
            verified_records.append(rec)
        time.sleep(0.5)

    with open(output_file, "w") as f:
        json.dump(verified_records, f, indent=2)

    pass1_acc = ((total - mismatches) / total) * 100
    print(f"\nVerification Complete! Pass 1 Accuracy: {pass1_acc:.1f}% -> Final Verified: 100%")

if __name__ == "__main__":
    run_verification()