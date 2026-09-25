"""Groq connectivity + end-to-end AI check. Run from backend/:  python check_groq.py

- No key  -> confirms heuristic-fallback path works offline.
- With key -> lists Groq models, verifies primary/fallback ids exist,
  runs one LangGraph analysis and prints provider/severity.
"""
import json
import urllib.request

from app.config import settings
from app.services.ai_graph import analyze_deviation


def groq_models(api_key: str) -> list:
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return sorted(m["id"] for m in data.get("data", []))


def main() -> None:
    print(f"groq_configured : {bool(settings.groq_api_key)}")
    print(f"primary model   : {settings.groq_model}")
    print(f"fallback model  : {settings.groq_fallback_model}")
    if settings.groq_api_key:
        try:
            ids = groq_models(settings.groq_api_key)
            print(f"models on key   : {len(ids)}")
            for m in (settings.groq_model, settings.groq_fallback_model):
                print(f"  {'OK ' if m in ids else 'MISSING '} {m}")
        except Exception as e:
            print(f"models endpoint failed: {e}")
    else:
        print("no GROQ_API_KEY in .env -> heuristic-fallback expected")

    with open("../sample-documents/deviation-email-01.txt", encoding="utf-8") as f:
        text = f.read()
    out = analyze_deviation(text)
    print(f"provider        : {out['provider']}")
    print(f"severity        : {out['severity']}")
    print(f"batch           : {out['extracted'].get('batch_no')}")
    print(f"reason          : {out['ai_reason'][:120]}")


if __name__ == "__main__":
    main()
