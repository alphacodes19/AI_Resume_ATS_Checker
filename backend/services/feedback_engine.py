# this part tell what exactly is wrong in our resume

import re
from typing import List, Dict, Any, Optional
from backend.models.schemas import IssueDetail

def analyze_issues(
    resume_text: str,
    parsed_resume: Dict,
    skills: List[str],
    projects: List[Dict],
    action_verbs: List[str],
    skill_validation: Dict,
    scores: Dict,
    contact_info: Optional[Dict] = None,
) -> List[IssueDetail]:
    
    detected: List{IssueDetail} = []