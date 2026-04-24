import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

#Takes meeting notes as input and sends a request to the GROQ API to generate a structured Jira task. It constructs a prompt for the AI, makes the API call, and processes the response to extract the relevant information for creating a Jira issue. If the response is not valid JSON, it falls back to a default structure with manual review needed.
def call_groq(minutes: str) -> dict:
    prompt = f"""You MUST return ONLY valid JSON. No markdown. No explanation. No extra text.
    {{
        "title": "...",
        "issue_type": "Story|Bug|Feature|Chore",
        "description": "...",
        "acceptance_criteria": ["...", "...", "..."],
        "priority": "Low|Medium|High"
    }}
    Meeting notes:{minutes}"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": groq_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a backend engineering assistant. Return only valid JSON. Do not include markdown.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )

    print("GROQ STATUS:", response.status_code)
    print("GROQ RAW RESPONSE:", response.text)

    response.raise_for_status()

    data = response.json()
    raw_text = data["choices"][0]["message"]["content"].strip()

    try:
        return json.loads(raw_text)
    except Exception:
        print("⚠️ Groq returned non-JSON:", raw_text)
        return {
            "title": minutes[:100],
            "issue_type": "Story",
            "description": minutes,
            "acceptance_criteria": ["Manual review needed"],
            "priority": "Medium",
        }


def call_groq_simple(text: str) -> str:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": groq_model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text},
            ],
            "temperature": 0.7,
        },
        timeout=30,
    )

    data = response.json()
    return data["choices"][0]["message"]["content"]


def classify_user_intent(text: str) -> dict:
    prompt = f"""
Classify the user's message.

Return ONLY valid JSON:
{{
  "intent": "chat|create_jira",
  "reason": "short reason"
}}

User message:
{text}
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": groq_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You classify user intent. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        },
        timeout=30,
    )

    response.raise_for_status()
    raw_text = response.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(raw_text)
    except Exception:
        return {"intent": "chat", "reason": "fallback"}
