import re
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional, Tuple


from backend.utils.file_utils import log_warning
from backend.core.config import SENTENCE_TRANSFORMER_MODEL
from backend.utils.matching import fuzzy_match_keywords


ZIP_CODE_PATTERN = r'\b\d{5}(?:-\d{4})?\b'

STREET_ADDRESS_PATTERN = (
    r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+'
    r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\b'
)


def _tier_score(n: float, tiers:list) -> float:
    for threshold, pts in tiers:
        if n >= threshold:
            return pts
        
        return 0.0
    
#Location/privacy detection
def detect_location_info(text: str, nlp: spacy.Language) -> Dict:
    locations = []

    #method01: spacy NER
    
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            locations.append({'text': ent.text, 'type': ent.label_.lower(), 'start': ent.start_char})

    #moetod02: street address regx
    
    for match in re.finditer(STREET_ADDRESS_PATTERN, text, re.IGNORECASE):
        locations.append({'text': match.group(), 'type': 'address', 'start': match.start()})

    #method03: ZIP/PIN CODE REGEX PATTERN
    
    for match in re.finditer(ZIP_CODE_PATTERN, text):
        locations.append({'text': match.group(), 'type': 'zip', 'start': match.start()})

    has_address = any(loc['type'] == 'address' for loc in locations)
    has_zip     = any(loc['type'] == 'zip'     for loc in locations)

    if has_address and has_zip:
        privacy_risk, penalty = 'high', 5.0
    elif has_address or has_zip:
        privacy_risk, penalty = 'high', 4.0
    elif len(locations) > 3:
        privacy_risk, penalty = 'medium', 3.0
    elif locations:
        privacy_risk, penalty = 'low', 2.0
    else:
        privacy_risk, penalty = 'none', 0.0

    recommendations = []
    if not locations:
        recommendations.append(" No privacy concerns detected.")
    if has_address:
        recommendations.append(" Remove full street addresses — ATS systems don't need this and it's a privacy risk.")
    if has_zip:
        recommendations.append(" Remove zip codes — this level of location detail is unnecessary.")
    if privacy_risk in ('low', 'medium') and not has_address and not has_zip:
        recommendations.append(" Consider reducing location mentions. 'City, State' in the contact header is sufficient.")

    return {
        'location_found':     len(locations) > 0,
        'detected_locations': locations,
        'privacy_risk':       privacy_risk,
        'recommendations':    recommendations,
        'penalty_applied':    penalty,
    }
    
    
def _calculate_semantic_similarity(skill: str, text: str, embedder: SentenceTransformer) -> float:
    #similarity = (A · B) / (|A| × |B|)
    if not skill or not text:
        return 0.0
    try:
        skill_vec  = embedder.encode(skill, convert_to_tensor=False)
        text_vec   = embedder.encode(text,  convert_to_tensor=False)

        similarity = np.dot(skill_vec, text_vec) / (
            np.linalg.norm(skill_vec) * np.linalg.norm(text_vec)
        )

        return float(max(0.0, min(1.0, similarity)))
    except Exception as e:
        log_warning(f"Similarity error for '{skill}': {e}", context='ats_scorer')
        return 0.0


def _skill_matches(skill: str, text: str, embedder: SentenceTransformer, threshold: float) -> Tuple[bool, float]:

    #fast, o(n) directly check if skill is a substring of the text (case-insensitive)
    if skill.lower() in text.lower():
        return True, 1.0
    
    #slow, semantic similarity check using sentence embeddings
    sim = _calculate_semantic_similarity(skill, text, embedder)
    return sim >= threshold, sim

#Skill validation
def validate_skills_with_projects(
    skills: List[str],
    projects: List[Dict],
    experience_entries: List[Dict],
    embedder: SentenceTransformer,
    threshold: float = 0.6,
) -> Dict:
    
    if not skills:
        return {
            'validated_skills':      [],
            'unvalidated_skills':    [],
            'validation_percentage': 0.0,
            'skill_project_mapping': {},
            'validation_score':      0.0,
        }

    experience_text = ' '.join(
        f"{e.get('job_title', '')} {e.get('company', '')} {e.get('description', '')}"
        for e in experience_entries
        if isinstance(e, dict)
    ).strip()

    validated_skills      = []
    unvalidated_skills    = []
    skill_project_mapping = {}

    for skill in skills:
        matching_projects = []
        max_similarity    = 0.0

        for project in projects:
            project_text = f"{project.get('title', '')} {project.get('description', '')}"
            matched, sim = _skill_matches(skill, project_text, embedder, threshold)
            max_similarity = max(max_similarity, sim)

            if matched:
                matching_projects.append(project.get('title', 'Untitled Project'))

        if experience_text:
            matched, sim = _skill_matches(skill, experience_text, embedder, threshold)
            max_similarity = max(max_similarity, sim)
            if matched and 'Experience Section' not in matching_projects:
                matching_projects.append('Experience Section')

        if matching_projects:
            validated_skills.append({'skill': skill, 'projects': matching_projects, 'similarity': max_similarity})
            skill_project_mapping[skill] = matching_projects
        else:
            unvalidated_skills.append(skill)
            skill_project_mapping[skill] = []

    validation_percentage = len(validated_skills) / len(skills)
    validation_score      = validation_percentage * 15.0

    return {
        'validated_skills':      validated_skills,
        'unvalidated_skills':    unvalidated_skills,
        'validation_percentage': validation_percentage,
        'skill_project_mapping': skill_project_mapping,
        'validation_score':      validation_score,
    }


