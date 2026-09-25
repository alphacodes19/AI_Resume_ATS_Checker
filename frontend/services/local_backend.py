"""
Runs the analysis pipeline in-process, inside the Streamlit app itself,
instead of calling out to a separate FastAPI server over HTTP.

Why: the FastAPI backend needs torch + spaCy + sentence-transformers loaded
in memory, which needs more RAM than most free container hosts offer without
billing. Streamlit Community Cloud's free tier already has enough headroom
for these models (confirmed — the combined requirements.txt installs and
runs fine there), so we skip the second host entirely and call the same
backend service functions directly instead of over the network.

Mirrors backend/api/routes.py's logic exactly, just synchronous and without
the FastAPI request/response plumbing.
"""
import asyncio
import logging
from typing import Any, Dict, List

import streamlit as st

logger = logging.getLogger("ats_resume_scorer")


def _run_async(coro):
    """Run an async backend coroutine from Streamlit's sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Shouldn't happen under Streamlit's script runner, but just in case.
            import nest_asyncio  # type: ignore
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
    except RuntimeError:
        pass
    return asyncio.run(coro)


@st.cache_resource(show_spinner="Loading NLP models (first run only, ~30s)...")
def _load_models():
    from backend.core.config import SPACY_MODEL_PRIMARY, SPACY_MODEL_SECONDARY, SENTENCE_TRANSFORMER_MODEL

    import spacy
    try:
        nlp = spacy.load(SPACY_MODEL_PRIMARY)
        logger.info(f"Loaded {SPACY_MODEL_PRIMARY}")
    except OSError:
        nlp = spacy.load(SPACY_MODEL_SECONDARY)
        logger.info(f"Loaded {SPACY_MODEL_SECONDARY} (fallback)")

    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    logger.info(f"Loaded {SENTENCE_TRANSFORMER_MODEL}")

    return nlp, embedder


def health_check() -> Dict[str, Any]:
    nlp, embedder = _load_models()
    return {"status": "healthy", "nlp_loaded": nlp is not None, "embedder_loaded": embedder is not None}


def analyze_resume(resume_file, user_id: str, job_description: str = "") -> Dict[str, Any]:
    from backend.services.resume_parser import parse_resume_file
    from backend.services.resume_analyzer import analyze_full_resume
    from backend.models.schemas import AnalysisResponse, ComponentScores, JDComparison, SkillValidationDetails

    nlp, embedder = _load_models()

    file_bytes = resume_file.getvalue()
    filename = resume_file.name or "resume"

    resume_text, _metadata = parse_resume_file(file_bytes, filename)
    logger.info(f"Parsed '{filename}': {len(resume_text)} chars extracted")

    result = analyze_full_resume(
        resume_text=resume_text,
        nlp=nlp,
        embedder=embedder,
        job_description=job_description,
    )

    jd_comparison_result = None
    if result.get("jd_comparison"):
        jd_comparison_result = JDComparison(
            match_percentage=round(float(result["jd_comparison"].get("match_percentage", 0.0)), 1),
            semantic_similarity=round(float(result["jd_comparison"].get("semantic_similarity", 0.0)), 3),
            matched_keywords=result["jd_comparison"].get("matched_keywords", [])[:20],
            missing_keywords=result["jd_comparison"].get("missing_keywords", [])[:15],
            skills_gap=result["jd_comparison"].get("skills_gap", [])[:10],
        )

    svd_raw = result.get("skill_validation_details") or {}
    skill_val_details = SkillValidationDetails(
        validated=svd_raw.get("validated", []),
        unvalidated=svd_raw.get("unvalidated", []),
        total=svd_raw.get("total", 0),
        validated_count=svd_raw.get("validated_count", 0),
        validation_pct=svd_raw.get("validation_pct", 0.0),
    )

    response = AnalysisResponse(
        ATS_score=result["ats_score"],
        component_scores=ComponentScores(**result["component_scores"]),
        issues_summary=result["issues_summary"],
        detailed_feedback=result.get("detailed_feedback", []),
        jd_match_analysis=jd_comparison_result,
        skill_validation_details=skill_val_details,
        ats_score=result["ats_score"],
        keyword_match=jd_comparison_result.match_percentage if jd_comparison_result else 0.0,
        missing_keywords=result.get("missing_keywords", []),
        matched_keywords=result.get("matched_keywords", []),
        skills=list(result.get("skills", [])[:20]),
        jd_comparison=jd_comparison_result,
        interpretation=result.get("interpretation", ""),
    )

    try:
        from backend.database.supabase_db import save_analysis
        _run_async(save_analysis(user_id, filename, result))
    except Exception as exc:
        logger.warning(f"History save failed (non-blocking): {exc}")

    return response.model_dump()


def get_history(user_id: str) -> List[Dict[str, Any]]:
    from backend.database.supabase_db import get_user_history
    return _run_async(get_user_history(user_id))


def delete_history_entry(analysis_id: str, user_id: str) -> None:
    from backend.database.supabase_db import delete_analysis
    success = _run_async(delete_analysis(analysis_id, user_id))
    if not success:
        raise RuntimeError("Analysis not found or not owned by this user.")


def generate_pdf(analysis_data: Dict[str, Any]) -> bytes:
    from backend.services.report_generator import generate_html_reports
    from backend.services.pdf_export import generate_combined_pdf

    html_docs = generate_html_reports(analysis_data)
    return generate_combined_pdf(html_docs)


def get_history_pdf(analysis_id: str, user_id: str) -> bytes:
    from backend.services.report_generator import generate_html_reports
    from backend.services.pdf_export import generate_combined_pdf

    history = get_history(user_id)
    analysis_data = next((item["analysis_result"] for item in history if item["id"] == analysis_id), None)
    if not analysis_data:
        raise RuntimeError("Analysis not found")

    html_docs = generate_html_reports(analysis_data)
    return generate_combined_pdf(html_docs)
