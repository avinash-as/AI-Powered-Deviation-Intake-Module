import io
import re
from datetime import datetime


def extract_text_from_upload(filename: str, content: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n".join((p or "") for p in [pg.extract_text() for pg in reader.pages])
    # .txt, .eml, .md, .csv, .log, etc. -> decode
    for enc in ("utf-8", "latin-1"):
        try:
            return content.decode(enc)
        except Exception:
            continue
    return content.decode("utf-8", errors="ignore")


def heuristic_extract(text: str) -> dict:
    """Deterministic fallback so the demo works without a GROQ_API_KEY."""
    def find(patterns, default=""):
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE | re.MULTILINE)
            if m:
                return m.group(1).strip()
        return default

    batch = find([r"batch\s*(?:no\.?|number)?\s*[:#-]?\s*([A-Za-z0-9\-/]+)"])
    product = find([r"\bproduct\s*:\s*([A-Za-z0-9 \-\(\)]+)", r"\bof\s+([A-Za-z][A-Za-z0-9 \-]*?API)\b"])
    observed_by = find([r"(?:reported by|observed by|raised by|\bfrom\b)\s*[:#-]?\s*([A-Za-z .]+)"])
    department = find([r"depart?ment\s*[:#-]?\s*([A-Za-z &]+)", r"\b(QA|QC|Production|Engineering|Warehouse)\b"])
    equipment = find([r"equipment\s*[:#-]?\s*([A-Za-z0-9 \-\/]+)", r"\b((?:reactor|drying oven|dryer|centrifuge|filter press|filter|autoclave|HPLC|GC)\s*[A-Za-z0-9\-\/ ]{0,20})", ])
    spec = find([r"\bspec(?:ification)?(?: limit| range)?\s*:\s*([^\n]+)", r"approved range\s*:\s*([^\n]+)"])
    observed = find([r"observed\s*:\s*([^\n]+)", r"recorded\s*(?:as|at)?\s*([^\n]+)"])
    date_m = re.search(r"(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text)
    date_observed = ""
    if date_m:
        try:
            from dateutil import parser as dparser

            date_observed = dparser.parse(date_m.group(1), dayfirst=False).strftime("%Y-%m-%d")
        except Exception:
            date_observed = date_m.group(1)
    if not date_observed:
        date_observed = datetime.utcnow().strftime("%Y-%m-%d")

    lowered = text.lower()
    if any(k in lowered for k in ["calibrat", "breakdown", "pump", "reactor fault", "sensor fail"]):
        dev_type = "Equipment"
    elif any(k in lowered for k in ["raw material", "excipient", "vendor", "incoming"]):
        dev_type = "Material"
    elif any(k in lowered for k in ["sop", "document", "entry error", "logbook"]):
        dev_type = "Documentation"
    elif any(k in lowered for k in ["humidity excursion", "cleanroom", "hvac", "environmental monitoring"]):
        dev_type = "Environmental"
    else:
        dev_type = "Process"

    title = find([r"subject\s*[:#-]?\s*([^\n]+)", r"title\s*[:#-]?\s*([^\n]+)"])
    if not title:
        first = next((l.strip() for l in text.splitlines() if len(l.strip()) > 20), text[:80])
        title = f"Deviation — {first[:70]}"

    return {
        "title": title[:200],
        "description": text[:2000],
        "date_observed": date_observed,
        "observed_by": observed_by,
        "department": department or "Production",
        "product": product,
        "batch_no": batch,
        "stage": find([r"\bstag?e\s*:\s*([^\n]+)"]),
        "equipment": equipment,
        "specification_limit": spec,
        "observed_value": observed,
        "deviation_type": dev_type,
        "probable_cause": "",
        "immediate_action": find([r"(?:immediate action|action taken|contained by)\s*[:#-]?\s*([^\n]+)"]),
    }


def heuristic_severity(extracted: dict, text: str) -> dict:
    t = (text + " " + str(extracted)).lower()
    critical_keys = ["steril", "contaminat", "patient safety", "data integrity", "falsif", "adulterat"]
    major_keys = ["out of spec", "oos", "excursion", "outside", "exceed", "on hold", "rework", "reprocess",
                  "temperature", "pressure", "ph ", "yield", "impurity"]
    if any(k in t for k in critical_keys):
        return {"severity": "Critical", "impact_assessment": "Potential direct impact on patient safety / sterility assurance. Batch on hold; QA + investigations required.",
                "capa_required": True, "ai_reason": "Keywords indicate safety/sterility/data-integrity risk, which maps to Critical per GMP.", "ai_confidence": 0.72}
    if any(k in t for k in major_keys):
        return {"severity": "Major", "impact_assessment": "Process parameter excursion outside approved range. Potential quality impact — batch on hold pending QA review and CAPA evaluation.",
                "capa_required": True, "ai_reason": "Parameter excursion language suggests potential product-quality impact, hence Major with CAPA.", "ai_confidence": 0.78}
    return {"severity": "Minor", "impact_assessment": "Limited or no foreseeable product impact; document, correct and trend.",
            "capa_required": False, "ai_reason": "No safety or specification-impact signals detected; Minor is appropriate.", "ai_confidence": 0.65}
