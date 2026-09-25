from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import AnalyzeRequest, AnalyzeResponse, ExtractedDeviation
from ..services.ai_graph import analyze_deviation
from ..services.document_parser import extract_text_from_upload

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if len(req.text.strip()) < 10:
        raise HTTPException(400, "Please paste at least a few words of deviation text.")
    out = analyze_deviation(req.text)
    merged = {**out["extracted"],
              "severity": out["severity"],
              "impact_assessment": out["impact_assessment"],
              "ai_reason": out["ai_reason"],
              "ai_confidence": out["ai_confidence"],
              "capa_required": out["capa_required"]}
    # keep only ExtractedDeviation fields
    allowed = set(ExtractedDeviation.model_fields.keys())
    extracted = {k: v for k, v in merged.items() if k in allowed}
    return {
        "extracted": extracted,
        "severity": out["severity"],
        "impact_assessment": out["impact_assessment"],
        "ai_reason": out["ai_reason"],
        "ai_confidence": out["ai_confidence"],
        "provider": out["provider"],
        "raw_text_chars": len(req.text),
    }


@router.post("/analyze-file", response_model=AnalyzeResponse)
async def analyze_file(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 5 MB).")
    try:
        text = extract_text_from_upload(file.filename or "upload.txt", content)
    except Exception as e:
        raise HTTPException(400, f"Could not parse file: {e}")
    if len(text.strip()) < 10:
        raise HTTPException(400, "No readable text found in file.")
    return await _analyze_text(text)


async def _analyze_text(text: str):
    out = analyze_deviation(text)
    allowed = set(ExtractedDeviation.model_fields.keys())
    merged = {**out["extracted"], "severity": out["severity"],
              "impact_assessment": out["impact_assessment"], "ai_reason": out["ai_reason"],
              "ai_confidence": out["ai_confidence"], "capa_required": out["capa_required"]}
    return {
        "extracted": {k: v for k, v in merged.items() if k in allowed},
        "severity": out["severity"],
        "impact_assessment": out["impact_assessment"],
        "ai_reason": out["ai_reason"],
        "ai_confidence": out["ai_confidence"],
        "provider": out["provider"],
        "raw_text_chars": len(text),
    }
